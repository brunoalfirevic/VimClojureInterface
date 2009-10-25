import threading
import vim
import subprocess
import time

class SafeVim():
    main_vim_thread = threading.currentThread()
    vim_server_name = vim.eval("v:servername")
    
    def eval(self, expr):
        if threading.currentThread() == self.main_vim_thread:
            return vim.eval('%s' % expr)
        else:
            return self.__shell_vim_remote_expr('string(%s)' % expr)

    def command(self, cmd):
        if threading.currentThread() == self.main_vim_thread:
            vim.command(cmd)
        else:
            self.__shell_vim_remote_expr('Execute("%s")' % self.__argescape(cmd))

    def __shell_vim_remote_expr(self, expr):
        process = subprocess.Popen(['vim', '--remote-expr', expr, '--servername', self.vim_server_name], 
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output = process.communicate()
        return output[0].strip()

    @staticmethod
    def __argescape(arg):
        return arg.replace('"', '\\"')

vim.safe = SafeVim()
