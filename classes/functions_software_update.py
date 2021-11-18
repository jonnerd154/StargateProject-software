def software_update(current_version):
    """
    This functions tries to update the stargate program with new files listed in the database
    main.py must always be updated due to the version variable change in the file.
    The owner and group of the files is set to match the same as the current __file__ variable.
    If the requirements.txt file is updated the missing modules will be installed.
    :return: Nothing is returned.
    """
    import pymysql, dbinfo, requests, pwd, grp, sys, subprocess
    from os import stat, makedirs, path
    from base64 import b64decode
    from ast import literal_eval
    from pathlib import Path

    ## Some needed variables
    update_found = None
    base_url = 'https://thestargateproject.com/stargate_software_updates/'
    root_path = Path(__file__).parent.absolute()
    # get the user ID and group ID of the owner of this file (__file__). (In most instances this would result in the UID 1001 for the sg1 user.
    uid = pwd.getpwnam(pwd.getpwuid(stat(__file__).st_uid).pw_name).pw_uid
    gid = grp.getgrnam(pwd.getpwuid(stat(__file__).st_uid).pw_name).gr_gid

    ### Get the information from the DB ###
    db = pymysql.connect(host=dbinfo.db_host, user=dbinfo.db_user, password=str(b64decode(dbinfo.db_pass), 'utf-8'), database=dbinfo.db_name)
    cursor = db.cursor()
    sql = f"SELECT * FROM `software_update`"
    cursor.execute(sql)
    sw_update = cursor.fetchall()
    db.close()

    ## check the db information for a new update
    for entry in sw_update:

        ## if there is a newer version:
        if entry[1] > current_version:
            update_audio = play_random_audio_clip(str(root_path / "soundfx/update/"))
            update_found = True
            print(f'Newer version {entry[1]} detected!')
            log('sg1.log', f'Newer version {entry[1]} detected!')

            new_files = literal_eval(entry[2]) # make a list of the new files
            # Get the new files
            for file in new_files:
                r = requests.get(base_url + str(entry[1]) + '/' + file, auth=('Samantha', 'CarterSG1!')) # get the file
                filepath = Path.joinpath(root_path, file) # the path of the new file
                try:
                    makedirs(path.dirname(filepath)) # create directories if they do not exist:
                except:
                    pass
                open(filepath, 'wb').write(r.content) # save the file
                os.chown(str(root_path / file), uid, gid) # Set correct owner and group for the file
                print (f'{file} is updated!')
                log('sg1.log', f'{file} is updated!')

                #If requirements.txt is new, run install of requirements.
                if file == 'requirements.txt':
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", Path.joinpath(root_path, 'requirements.txt')])
            # Don't cut the update audio short the update
            if update_audio.is_playing():
                update_audio.wait_done()
    if update_found:
        log('sg1.log', 'Update installed -> restarting the program')
        print('Update installed -> restarting the program')
        os.execl(sys.executable, *([sys.executable] + sys.argv))  # Restart the program
