from crack import celery_app
# import shlex
import subprocess
import logging


def run_shell_command1(hash):
    try:
        command_line_process = subprocess.Popen(
            "df -h",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        for l in iter(command_line_process.stdout.readline, b''):
            logging.info(l.strip())

        command_line_process.communicate()
        command_line_process.wait()

    except (OSError, subprocess.CalledProcessError) as exception:
        logging.info('Exception occured: ' + str(exception))
        logging.info('Subprocess failed')
        return False
    else:
        # no exception was raised
        logging.info('Subprocess finished')

    return True


def run_shell_command2(hash):
    try:
        command_line_process = subprocess.run(["curl", "-I","www.google.com"], check=False, capture_output=True, text=True)
        # for l in iter(command_line_process.stdout, b''):
        #     logging.info(l.strip())
        value = command_line_process.stdout.splitlines()
        for line in value:
            logging.info(line.strip())

    except (OSError, subprocess.CalledProcessError) as exception:
        logging.info('Exception occured: ' + str(exception))
        logging.info('Subprocess failed')
        return False
    else:
        # no exception was raised
        logging.info('Subprocess finished')

    return True


@celery_app.task
def pojie(hash):
    run_shell_command2(hash)
    print("crack with hash key:" + hash + " ok done!")
    return "this is result"
