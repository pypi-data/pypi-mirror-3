import subprocess

def shargs(args):
    process = subprocess.Popen('for arg in %s; do echo $arg; done' % args,
                               shell=True, stdout=subprocess.PIPE)
    output = process.communicate()[0]
    output = output[:-1] # last line will be blank
    return output.split('\n')
