import vim
import threading
import subprocess

class SafeVim():
    main_vim_thread = threading.currentThread()
    vim_server_name = vim.eval("v:servername")
    
    def eval_as_string(self, expr):
        if threading.currentThread() == self.main_vim_thread:
            return vim.eval("remote_expr(v:servername, 'string(%s)')" % self.__argescape(expr))
        else:
            return self.__shell_vim_remote_expr("string(%s)" % expr)

    def command(self, cmd):
        if threading.currentThread() == self.main_vim_thread:
            vim.eval("remote_expr(v:servername, 'ExecuteForSafeVim(''%s'')')" % self.__argescape(self.__argescape(cmd)))
        else:
            self.__shell_vim_remote_expr("ExecuteForSafeVim('%s')" % self.__argescape(cmd))

    def __shell_vim_remote_expr(self, expr):
        process = subprocess.Popen(['vim', '--servername', self.vim_server_name, '--remote-expr', expr], 
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output = process.communicate()
        return output[0].strip()

    @staticmethod
    def __argescape(arg):
        return arg.replace("'", "''")

vim.command("function! ExecuteForSafeVim(cmd) \n execute a:cmd \n return '' \n endfunction")
vim.safe = SafeVim()
vim.eval_as_string = lambda expr: vim.eval('string(%s)' % expr)
