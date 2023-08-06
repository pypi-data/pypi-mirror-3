import inspect, argparse, new


def parser(description):

    def new_fn(fn):
        
        parser = register_parser(name=default_parser_name, description=description)

        def parse_commands(fn, group):
            commands =  {}
            class_functions = { x : fn.__dict__[x] for x in fn.__dict__ if inspect.isfunction(fn.__dict__[x]) }
       
            for cfn_name, cfn in class_functions.iteritems():
                if hasattr(cfn, "is_command") and cfn.is_command:
                    commands[cfn_name] = cfn
                    parser.add_command(cfn_name, cfn, group)
            return commands

        
        def parse_command_group(fn, group):
            class_classes = { x : fn.__dict__[x] for x in fn.__dict__ if inspect.isclass(fn.__dict__[x]) }
            for class_name, clazz in class_classes.iteritems():
                if hasattr(clazz, "is_command_group") and clazz.is_command_group:
                    parser.add_command_group(class_name, group=group )
                    parse_command_group(clazz, class_name)
                    
                    
            commands = parse_commands(fn, group)
                    
            
        
        parse_command_group(fn, None)
        
        parser.parse()
        return fn
        
    return new_fn

    
    
def command_group(fn, name=None):
    fn.is_command_group = True  
    return fn
  
def command(fn, name=None):
    fn.is_command = True
    return fn

def help(key, help=None):
    def decorator(fn):
        if help is None:
            fn.help = key
        else:
            if not hasattr(fn, "helps"):
                fn.helps = {}
            fn.helps[key] = help
        return fn
    return decorator
    
    
class AgreeParser(object):

    def __init__(self, description):
        self.arg_parse =  argparse.ArgumentParser(description=description)
        self.sub_groups = {}
        self.sub_groups[None] =  self.arg_parse.add_subparsers(help=None)
        self.groups = {}
    
    
    def add_command(self, name, fn, group=None):
        fnhelp = fn.help if hasattr(fn, "help") else None
        self.groups[name] = self.sub_groups[group].add_parser(name.lower(), help=fnhelp)
        argspec = inspect.getargspec(fn)
        
        def generate_shorts(spec):
            shorts = {}
            for arg in spec.args:
                letters = arg[0:1]
                for x in range(0, len(spec.args)):
                    other_arg = spec.args[x]
                    default_index = x - (len(argspec.args) - len(argspec.defaults)) 
                    if default_index >= 0:
                        if other_arg != arg:
                            for i in range(0, len(other_arg)):
                                if letters == other_arg[0:i+1]:
                                    letters = arg[0:i+2]
                                else:
                                    break
                    
                shorts[arg] = '-' + letters
            return shorts
        
        shorts = generate_shorts(argspec)

        
        for x in range(0, len(argspec.args)):
            arg = argspec.args[x]
            default = None
            default_index = x - (len(argspec.args) - len(argspec.defaults)) 
            if default_index < len(argspec.defaults) and default_index >= 0:
                default = argspec.defaults[default_index]
            
            help = None
            if hasattr(fn, "helps") and arg in fn.helps:
                help = fn.helps[arg]
          
           # print str(x) + ": " + str(default) + ": " + arg
            #if default is not None:
             #   print default.__dict__
             
            
            short = shorts[arg] if default is not None else None
            
            
            arg_name = ('--' + arg if default is not None else arg)
        
            
            
             
            if isinstance(default, ArgWrapper):
                wrapper = default
                
                help = default.help if help is None else help
                
                dest = arg if default.dest is None else default.dest
                
                # There's got to be a better way to do this...too many if statements!
                
                if wrapper.action == "store_true" or wrapper.action == "store_false":
                    if short is not None:
                        self.groups[name].add_argument(arg_name, short, action=wrapper.action, 
                        default=wrapper.default, required=wrapper.required, 
                        help=help,  dest=dest)
                    else:
                        self.groups[name].add_argument(arg_name,  action=wrapper.action, 
                        default=wrapper.default, required=wrapper.required, 
                        help=help,  dest=dest)
                elif wrapper.action == "store_const":
                    if short is not None:
                        self.groups[name].add_argument(arg_name, short,action=wrapper.action, 
                        default=wrapper.default, required=wrapper.required, const=wrapper.const,
                        help=help,  dest=dest)
                    else:
                        self.groups[name].add_argument(arg_name,action=wrapper.action, 
                        default=wrapper.default, required=wrapper.required, const=wrapper.const,
                        help=help,  dest=dest)
                
                elif wrapper.action == "count":
                    if short is not None:
                        self.groups[name].add_argument(arg_name, short,action=wrapper.action, 
                        default=wrapper.default, required=wrapper.required, 
                        help=help,  dest=dest)
                    else:
                        self.groups[name].add_argument(arg_name,action=wrapper.action, 
                        default=wrapper.default, required=wrapper.required,
                        help=help,  dest=dest)
                
                else:
                    if short is not None:
                        self.groups[name].add_argument(arg_name,short, action=wrapper.action, nargs=wrapper.nargs, const=wrapper.const, 
                    default=wrapper.default, type=wrapper.type, choices=wrapper.choices, required=wrapper.required, 
                    help=help, metavar=wrapper.metavar, dest=dest)
                    else:
                        self.groups[name].add_argument(arg_name, action=wrapper.action, nargs=wrapper.nargs, const=wrapper.const, 
                    default=wrapper.default, type=wrapper.type, choices=wrapper.choices, required=wrapper.required, 
                    help=help, metavar=wrapper.metavar, dest=dest)
            else:
                if short is not None:
                    self.groups[name].add_argument(arg_name, short, default=default,
                  help=help)
                else:
                    self.groups[name].add_argument(arg_name, default=default,
                  help=help)   
                  
        self.groups[name].set_defaults(command=fn)
    
    def add_command_group(self, name, help=None, group=None):
        self.groups[name] = self.sub_groups[group].add_parser(name.lower(), help=None)
        self.sub_groups[name] = self.groups[name].add_subparsers(help=None)
    
    def parse(self):
        parsed = self.arg_parse.parse_args()
        arg_info = inspect.getargspec(parsed.command)
        keywords = {}
        
      
        for x in arg_info.args:
            keywords[x] = parsed.__dict__[x]
        parsed.command(**keywords)
 
class ArgWrapper(object):


    def __init__(self, name, action="store", nargs=1, const=None, default=None, type=str, choices=None, required=False, help="", metavar=None, dest=None):
        self.name = name
        self.action = action
        self.nargs = nargs
        self.const = const
        self.default = default
        self.type = type
        self.choices = choices
        self.required = required
        self.help = help
        self.metavar = metavar
        self.dest = dest
        
    def __str__(self):
        return self.action
    def __repr__(self):
        return self.__str__()


#ArgWrapper Convenience Methods

def store_const(default=None, const=None, dest=None):
    return ArgWrapper(None, action="store_const", dest=dest, default=default, const=const)
    
    
def store(default=None, const=None, dest=None, nargs=1):
    return ArgWrapper(None, action="store", dest=dest, default=default, const=const, nargs=nargs)

def store_true(default=True, dest=None):
    return ArgWrapper(None, action="store_true", dest=dest, default=default)
    
def store_false(default=False, dest=None):
    return ArgWrapper(None, action="store_false", dest=dest, default=default)

def append(default=0, dest=None):
    return ArgWrapper(None, action="append", dest=dest, default=default)
    
def append_const(default=0, dest=None, const=None):
    return ArgWrapper(None, action="append_const", dest=dest, const=const, default=default)
    
def count(default=0, dest=None):
    return ArgWrapper(None, action="count", dest=dest, default=default)
    
parsers = {}
default_parser_name = "agree_default"

def register_parser(name, description=None):
    parsers[name] = AgreeParser(description)
    return parsers[name]
