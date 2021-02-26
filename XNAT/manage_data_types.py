#!/usr/bin/env python3
'''
Add or update XNAT data types using settings provided in JSON file. Checks
current XNAT data type settings to detemine if types need to be added or
updated.
'''
import argparse, json, lxml.html, re, requests

data_t_pref = 'xdat:security/element_security_set/element_security'
data_t_add_pref = 'xdat:element_security.'

def getShortXnatKeys(data_t_xnat):
    '''remove long name prefixes retrieved from web form'''
    rep = re.compile('^'+data_t_pref+'[[](?P<id>[^]]*)[]]/(?P<key>.*)$')
    data_t_xnat_short = []
    for row in data_t_xnat:
        data_t_xnat_short.append({})
        for k, v in row.items():
            m = rep.match(k)
            key, row_id = m.group('key'), m.group('id')
            data_t_xnat_short[-1][key] = v
            if row_id in data_t_xnat_short[-1]:
                if data_t_xnat_short[-1]['id'] != row_id:
                    raise Exception('row id error in xnat data types: {}'.format(row_id))
            else:
                data_t_xnat_short[-1]['id'] = row_id
    return data_t_xnat_short

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('-s', '--siteurl', required=True, help='Site URL (http[s]://<host>[:<port>])')
parser.add_argument('-u', '--user', required=True, help='Username')
parser.add_argument('-p', '--passwd', required=True, help='Password')
parser.add_argument('-f', '--configfile', required=True, help='Configuration JSON file')

args = parser.parse_args()

siteurl = args.siteurl.rstrip('/')
user = args.user
passwd = args.passwd
configfile = args.configfile

headers = {'Content-Type': 'application/json', 'Accept': '*/*'}
headers_post = headers.copy()
headers_post['Content-Type'] = 'application/x-www-form-urlencoded'

with open(configfile, 'r') as f:
    data_t_cfg = json.load(f)

try:
    print('opening XNAT session...')
    s = requests.session()
    urlJS = siteurl + '/data/JSESSION'
    response = s.post(urlJS, headers=headers, auth=requests.auth.HTTPBasicAuth(user, passwd))
    response.raise_for_status()

    print('retrieving data types...')
    url = siteurl + '/app/action/ManageDataTypes'
    response = s.get(url, headers=headers)
    response.raise_for_status()
    # print(response.headers)
    # print(response.text)
except Exception as e:    
    print('Error occurred: {}'.format(e))
    exit(1)

# extract csrf token from page for use in subsequent post requests
res = ".* csrfToken = '(?P<tok>[^']*)'.*"
m = re.match(res, response.text, flags=re.MULTILINE|re.DOTALL)
try:
    csrfToken = m.group('tok')
except AttributeError:
    raise Exception('csrfToken not found')

data_t_xnat = []
try:
    # parse data type settings from retrieved data-type-table
    root = lxml.html.fromstring(response.content)
    for tr in root.xpath('//table[@id="data-type-table"]//tr'):
        row = {}
        for td in tr.xpath('.//td'):
            for inp in td.xpath('.//input'):
                att = inp.attrib
                if att['type'] == 'checkbox':
                    row[att['name']] = 'false' if att.get('checked') is None else 'true'
                else:
                    row[att['name']] = att['value'] 
        if len(row) > 0:
            data_t_xnat.append(row)
except Exception as e:
    raise Exception('error parsing xnat data types: {}'.format(s))

# compare configfile settings with retrieved settings
data_t_xnat_short = getShortXnatKeys(data_t_xnat)
xnat_elem_names = [d['element_name'] for d in data_t_xnat_short]
updates = []
for cfg in data_t_cfg:
    try:
        row = xnat_elem_names.index(cfg['element_name'])
    except ValueError:
        updates.append({ cfg['element_name']: None })
        continue
    update_row = None
    for col in cfg:
        if cfg[col] != data_t_xnat_short[row][col]:
            update_row = data_t_xnat_short[row]['id']
            break
    if update_row is not None:
        updates.append({ cfg['element_name']: update_row })

# generate post data for added and for updated data types
dataAdd, dataUpdate, update_num = [], {}, 0
for update in updates:
    for name, row_id in update.items():
        update_cfg = None
        for cfg in data_t_cfg:
            if name == cfg['element_name']:
                update_cfg = cfg
                break
        pref = data_t_add_pref if row_id is None else data_t_pref+'['+row_id+']/'
        data = {pref+k: v for k, v in update_cfg.items()}
        if row_id is None:
            dataAdd.append(data)
        else:
            dataUpdate.update(data)
            update_num += 1

# post updates in one request
url = siteurl + '/app/action/ManageDataTypes'
if update_num > 0:
    dataUpdate['XNAT_CSRF'] = csrfToken
    try:
        print('updating {} data type{}...'.format(update_num, '' if update_num == 1 else 's'))
        response = s.post(url, headers=headers_post, data=dataUpdate)
        response.raise_for_status()
        # print(response.request.headers)
        # print(response.request.body)
    except Exception as e:    
        print('Error occurred: {}'.format(e))
        exit(1)

# post adds in separate requests
url = siteurl + '/app/action/ElementSecurityWizard'
for data in dataAdd:
    name = data_t_add_pref+'element_name'
    psf = 'primary_security_field'
    data['xml'] = '1',
    data['edit'] = '1',
    data['email_report'] = '1',
    data['activate'] = '0',
    data[data_t_add_pref+psf+'s.'+psf+'__0.'+psf] = data[name]+'/project',
    data[data_t_add_pref+psf+'s.'+psf+'__1.'+psf] = data[name]+'/sharing/share/project',
    data[data_t_add_pref+'secondary_password'] = '0',
    data[data_t_add_pref+'secure_ip'] = '0',
    data[data_t_add_pref+'quarantine'] = '0',
    data[data_t_add_pref+'pre_load'] = 'false',
    data[data_t_add_pref+'usage'] = '',
    data[data_t_add_pref+'category'] = '',
    data['eventSubmit_doStep3'] = 'Next',
    data['XNAT_CSRF'] = csrfToken
    try:
        print('adding data type {}...'.format(data[name]))
        response = s.post(url, headers=headers_post, data=data)
        response.raise_for_status()
    except Exception as e:    
        print('Error occurred: {}'.format(e))
        exit(1)

try:
    print('closing XNAT session...')
    response = s.delete(urlJS, headers=headers)
    response.raise_for_status()
except Exception as e:    
    print('Error occurred: {}'.format(e))
    exit(1)

exit(0)
