def setLog(program_name = '', date_format = ['%Y', '%m'], log_dir = 'logs/', log_ext = '.log'):
    '''
        This function sets up an easy-to-use logger.

        It sets up a log filename based on the current month and program name.
        The default log directory is 'logs,' relative to current directory.
        The function will try to create the directory if it doesn't exist.

        Name:       Logger
        Creator:    Matt Gagnon <mgagnon@ecoastsales.com>
        Created:    2012-05-10
        Revised:    2012-08-23 (added date_format to parameters,
                    more robust error checking)
        Version:    1.1
        Python:     2.6
        Example:    main = setLog()
                    main.error('log an error')
                    main.warning('log a warning')
                    main.info('log information')
    '''

    # import native python modules
    import time, datetime, logging, os, errno

    # check if the log directory does not have an ending slash
    if len(log_dir) <> 0:
        if log_dir[len(log_dir) - 1] != '/':
            # add a slash
            log_dir = log_dir + '/'

        try:
            # try to create the directory if it doesn't exist
            os.makedirs(log_dir)
        except OSError, e:
            # catch errors and raise them
            if e.errno != errno.EEXIST:
                raise

    # create a log object
    log = logging.getLogger(program_name)

    # set up a list of valid date format codes
    valid_format_codes = ['%a', '%A', '%b', '%B', '%c', '%d', '%f', '%H', '%I', '%j', '%m', '%M', '%p', '%S', '%U', '%w', '%W', '%x', '%X', '%y', '%Y', '%z', '%Z', '%%']
    valid_codes = ''

    try:
        # loop through all the codes in the date_format list
        for code in date_format:
            # check if the code is in our valid codes
            if code in valid_format_codes:
                # append a hyphen to it
                valid_codes += code+'-'
    except Exception, e:
        print 'Sorry, there was an error with the date format:',e

    # now create the date part of the filename
    date_time = datetime.datetime.now().strftime(valid_codes)

    filename = date_time+program_name
    filename = filename.strip('-')

    # check if the filename is blank
    if filename == '':
        # assign it a generic name
        filename = 'log'

    # assign the filename
    filename = log_dir+filename+log_ext

    # assign the filename to the file handler
    handler = logging.FileHandler(filename)

    # put our log record string together and assign to the formatter
    formatter = logging.Formatter('%(asctime)s %(levelname)s - %(message)s')

    # now set up our handler with that format
    handler.setFormatter(formatter)

    # add the file handler to our log object
    log.addHandler(handler)

    # set the logging level to info
    log.setLevel(logging.INFO)

    # return our log object
    return log
