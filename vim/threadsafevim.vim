py << EOF
import threading
import vim
import subprocess
import time

main_vim_thread = threading.currentThread()
vim_server_name = vim.eval("v:servername")

class SafeVim():
    def eval(self, expr):
        if threading.currentThread() == main_vim_thread:
            return vim.eval('%s' % expr)
        else:
            #return vim.eval(self.__shell_vim_remote_expr('string(%s)' % expr))
            return self.__shell_vim_remote_expr('string(%s)' % expr)

    def command(self, cmd):
        if threading.currentThread() == main_vim_thread:
            vim.command(cmd)
        else:
            self.__shell_vim_remote_expr('Execute("%s")' % self.__argescape(cmd))

    @staticmethod
    def __shell_vim_remote_expr(expr):
        process = subprocess.Popen(['vim', '--remote-expr', expr, '--servername', vim_server_name], 
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output = process.communicate()
        return output[0].strip()

    @staticmethod
    def __argescape(arg):
        return arg.replace('"', '\\"')

vim.safe = SafeVim()
EOF
