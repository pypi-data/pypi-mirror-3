import os
import re
import textwrap


class PythonSource(object):
    """
    Limited editing of Python source code.
    """
    
    def add_imports(self, *import_lines):
        """
        Add imports to Python source, after the first import section in the file
        if found. Fails on multi-line imports, but that's fine for our needs.
        """
        
        import_lines_end = None
        seen_import_lines = set()
        for index, line in enumerate(self.lines):
            if line.strip() == '' or line.startswith('#'):
                continue
            
            in_import = re.search(r'^(from|import)\s+', line) is not None
            
            if not in_import:
                break
            else:
                import_lines_end = index
                seen_import_lines.add(line.rstrip())
        
        if import_lines_end is None:
            prefix_lines = []
            suffix_lines = self.lines
        else:
            prefix_lines = self.lines[:import_lines_end+1]
            suffix_lines = self.lines[import_lines_end+1:]
        
        self.lines = prefix_lines + [
            import_line
            for import_line
            in import_lines
            if import_line not in seen_import_lines
        ] + suffix_lines
    
    def append_code(self, string):
        code_lines = self.lines_from_string(string)
        
        self.string = self.string.rstrip()
        
        if self.string != '':
            self.string += '\n\n\n'
        
        self.string += string.rstrip() + '\n'
    
    def dedent_and_append_code(self, string):
        string = textwrap.dedent(string)
        string = re.sub(r'^\s*\n', '', string)
        string = re.sub(r'\n\s*$', '', string)
        self.append_code(string)
    
    def replace_once(self, regex, replacement):
        self.string, subs = re.subn(regex, replacement, self.string, 1)
        if subs == 0:
            raise Exception('Couldn\'t find regex in string')
    
    @classmethod
    def file_edits(cls, filename, create_if_not_exists=False):
        class FileEdits(object):
            def __init__(self, filename, create_if_not_exists):
                self.filename = filename
                self.create_if_not_exists = create_if_not_exists
            
            def __enter__(self):
                try:
                    f = open(self.filename)
                except (IOError, OSError,):
                    if os.path.isfile(self.filename) or not self.create_if_not_exists:
                        raise
                    else:
                        self.source = cls.from_string('')
                else:
                    self.source = cls.from_file(f)
                
                return self.source
            
            def __exit__(self, type, value, traceback):
                open(self.filename, 'w').write(self.source.string)
        
        return FileEdits(filename, create_if_not_exists)
    
    @classmethod
    def from_file(cls, f):
        obj = cls()
        obj.string = f.read()
        return obj
    
    @classmethod
    def from_string(cls, string):
        obj = cls()
        obj.string = string
        return obj
    
    def _get_string(self):
        if not hasattr(self, '_string'):
            if not hasattr(self, '_lines'):
                return ''
            self._string = '\n'.join(self.lines)
        return self._string
    
    def _set_string(self, string):
        self._string = string
        if hasattr(self, '_lines'):
            del self._lines
    
    string = property(_get_string, _set_string)
    
    def _get_lines(self):
        if not hasattr(self, '_lines'):
            if not hasattr(self, '_string'):
                return []
            self._lines = self.lines_from_string(self.string)
        return self._lines
    
    def _set_lines(self, lines):
        self._lines = lines
        if hasattr(self, '_string'):
            del self._string
    
    lines = property(_get_lines, _set_lines)
    
    def lines_from_string(self, string):
        return re.findall(r'(?m)^.*$', string)
