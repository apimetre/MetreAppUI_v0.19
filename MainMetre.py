# Python imports
import os, requests, shutil, zipfile, json, sys, tempfile, fnmatch, console
from types import SimpleNamespace
from pprint import pprint

# Pythonista imports
import shortcuts
import qrcode
import requests

CONFIG_DICT = {'install_root_name': "MetreiOS",
                            'git_usr': "apimetre",
                            'git_repo': "MetreAppUI_v0.17",
                            'git_branch': "main",
                            'start_file': "MetreUI.py",
                            'is_release': "False",
                            'git_auth': "d6b3c5469d1e394f5b692dba9f01"
}



TEMPDIR = tempfile.mkdtemp()
def init_install_path(install_dir_name):
    root_dir = os.path.abspath(os.path.expanduser('~/Documents/' + install_dir_name))
    if os.path.exists(root_dir):
        update = True
        try:
        	with open(root_dir + '/metre_ios_install_config.json') as f:
        		config_dict = json.load(f)
        except:
        	with open(root_dir + '/metre_ios_install_config.json', 'w') as outfile:
        		json.dump(CONFIG_DICT, outfile)
        	config_dict = CONFIG_DICT
        
    else:
        print('making app directory')
        os.makedirs(root_dir, exist_ok=True)
        update = False
        with open(root_dir + 'metre_ios_install_config.json', 'w') as outfile:
        	json.dump(CONFIG_DICT, outfile)
        config_dict = CONFIG_DICT
        
    return root_dir, update, config_dict

#####

def make_git_url(usr, repo, branch):
    URL_TEMPLATE = 'https://github.com/{}/{}/archive/{}.zip'
    url = URL_TEMPLATE.format(usr, repo, branch)
    return url

def git_headers(git_pat):
    token = "token " + git_pat
    headers = {"Authorization": token}
    return headers
    
def getPrev(install_path, root_dir, fname):
# Look for previous versions
    sortedList = sorted([x for x in os.listdir(root_dir) if x.startswith('MetreAppUI')])
    print("this is the sorted list " + str(sortedList))
    #try:
    #    sortedList.remove(params['git_repo'])
    #except ValueError:
    #    pass
    prev_version = sortedList[-2]
    print('this is the previous version ', prev_version)
    print('about to name src_path')
    #print(root)
    src_path = root_dir + '/' + prev_version + '/log/' + fname
    print('THIS is the src path ' + src_path)
    print('This is where i am going to copy it to ' + install_path + '/log/' + fname)
    shutil.copy(src_path, install_path  + '/log/' + fname)

def install_from_github(root_path, install_path, auth_token, url, update_status, params):
    token_pyld = "token " + auth_token + 'a60ab710b075'
    headers = {"Authorization": token_pyld}
    dwnld_zipfile = '/'+ url.split('/')[-1]
    local_zipfile = install_path + dwnld_zipfile
    try:
        r = requests.get(url, stream=True, headers=headers)
        r.raise_for_status()
        with open(local_zipfile, 'wb') as f:
            block_sz = 1024
            for chunk in r.iter_content(block_sz):
                f.write(chunk)
        z = zipfile.ZipFile(local_zipfile)
        z.extractall(TEMPDIR)
        print('V11 speaking: These are the files in the tempdir')
        print('Update Status is ' + str(update_status))
        githubfolder = os.listdir(TEMPDIR)
        #print(os.listdir(TEMPDIR))
        print(githubfolder[0])
        print('These are the folders in tempdir/githubfolder')
        tempsource = TEMPDIR + '/' + githubfolder[0]
        print("THIS is tempsource " + str(tempsource))
        print("THIS is the destination " + str(install_path))
        print(os.listdir(tempsource))
        allFileList = os.listdir(tempsource)
        if not update_status:
            for file in allFileList:
                shutil.move(tempsource + '/' + file, install_path + '/' + file)
            
        else:
            for file in allFileList:
                print('This is the file i am looking at NOW!!!!' + file)
            
                if fnmatch.fnmatch(file, 'log'):
                    if os.path.exists(install_path + '/log/log_003.json'):
                        continue
                    else:
                        try:
                            if not os.path.exists(install_path + '/log'):
                            	os.makedirs(install_path + '/log')
                            getPrev(install_path, root_path, 'log_003.json')
                            getPrev(install_path, root_path, 'timezone_settings.json')
                            getPrev(install_path, root_path, 'device_settings.json')

                        except:
                            shutil.move(tempsource + '/' + file, install_path + '/' + file)
                            continue

                else:
                    shutil.move(tempsource + '/' + file, install_path + '/' + file)
                    continue

        unzipped_dirname = z.namelist()[0]
        os.remove(local_zipfile)
        installedFileList = os.listdir(install_path)
        print('finished listing')
        return installedFileList, githubfolder[0]
    except Exception as e:
        print(f"Install Error: {e}")
        return None

def install_branch(params):
    root_install_path, update_status, config_dict = init_install_path(params['install_root_name'])
    url = make_git_url(params['git_usr'], params['git_repo'], params['git_branch'])
    install_path = root_install_path + '/' + params['git_repo']
    installed_files, dirfromgit = install_from_github(root_install_path, install_path, params['git_auth'], url, update_status, params)
    print(f"\nUnzipping: {url}")
    pprint(installed_files)
    print()
    return install_path, url, installed_files, dirfromgit

def create_url_scheme_and_qr_code(installed_dir, url_scheme, start_file):
    url_file = start_file.split('.')[0] + '.url'
    open(installed_dir + url_file, "w").write(url_scheme)
    print(f"\nURL Scheme saved as: {url_file}")

    img = qrcode.make(url_scheme)
    img.show()
    qrcode_file = 'qrcode' + '-' + start_file.split('.')[0] + '.jpg'
    img.save(installed_dir + qrcode_file)
    print(f"\nQR Code saved as: {qrcode_file}")

def main():
    console.clear()
    install_path, update_status, config_dict =init_install_path(CONFIG_DICT['install_root_name'])
    current_install_path = os.path.abspath(os.path.expanduser('~/Documents/' + CONFIG_DICT['install_root_name'] + '/' + config_dict['git_repo']))
    if os.path.exists(current_install_path):
        # Code to launch app
        print("Launching MetreiOS app...one moment please")
        start_path = current_install_path + '/' + config_dict['start_file']
        url_scheme = shortcuts.pythonista_url(path=start_path, action='run', args="", argv=[])
        shortcuts.open_url(url_scheme)
    else:
    		
        os.makedirs(current_install_path)
        # Code to do install (for both Case 1 and Case 2)
        # Contains exceptions to handle previous versions
        install_path, url, installed_files, dirfromgit = install_branch(config_dict)
        # Case 1: Updating the app
        if update_status:
        	start_path = current_install_path + '/' +    config_dict['start_file']
        	print(start_path)
        	url_scheme = shortcuts.pythonista_url(path=start_path,  action='run', args="", argv=[])
        	console.clear()
        	print("Updating MetreiOS app...one moment please")
    
        	installed_dir = current_install_path + '/' + installed_files[0]
        	create_url_scheme_and_qr_code(installed_dir, url_scheme, config_dict['start_file'])
        	console.clear()
        	print("Update complete...Launching App")
	        shortcuts.open_url(url_scheme)
    
    	# Case 2: Installing app for the first time (update_status is false). Need to first run shortcut
        else:
        	console.clear()
        	print("Download in progress")
        	start_path = current_install_path + '/shortcut.py'
        	url_scheme = shortcuts.pythonista_url(path=start_path,  action='run', args="", argv=[])
        	#	print(f"\nURL scheme: {url_scheme}")
        	installed_dir = current_install_path + '/' + installed_files[0]
        	create_url_scheme_and_qr_code(installed_dir, url_scheme, 'shortcut.py')
        	console.clear()
        	print("Download complete---launching setup")
        	shortcuts.open_url(url_scheme)
 ###################################


 

if __name__ == '__main__':
    main()
