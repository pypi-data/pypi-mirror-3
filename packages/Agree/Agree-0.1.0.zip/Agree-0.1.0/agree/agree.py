import inspect, argparse, new



def parser(fn):

    def new_fn():
        
        parser = register_parser(name=default_parser_name)

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
    
    
    
class AgreeParser(object):

    def __init__(self, description):
        self.arg_parse =  argparse.ArgumentParser(description=description)
        self.sub_groups = {}
        self.sub_groups[None] =  self.arg_parse.add_subparsers(help='TODO HELP')
        self.groups = {}
    
    
    def add_command(self, name, function, group=None):
        self.groups[name] = self.sub_groups[group].add_parser(name, help='a help')
        self.groups[name].add_argument('integers', metavar='N', type=int, nargs='+',
                   help='an integer for the accumulator')
        self.groups[name].set_defaults(command=function)
    
    def add_command_group(self, name, group=None):
        self.groups[name] = self.sub_groups[group].add_parser(name, help='a help')
        self.sub_groups[name] = self.groups[name].add_subparsers(help='TODO HELP')
    
    def parse(self):
        print self.arg_parse.parse_args()
    
    
    

    
parsers = {}
default_parser_name = "agree_default"

def register_parser(name, description=None):
    parsers[name] = AgreeParser(description)
    return parsers[name]