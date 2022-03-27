class debugger:
    
    #TODO Support UART output possibly in signalk format

    def __init__(self, verbosity: int, enable: bool = False) -> None:
        """
        Enable or disable debugging output
        Verbosity: 0=basic debug messages, 1=most debug messages, 2=all debug messages. >0 adds 1 second sleep in program loop
        """
        self.enable = enable
        self.verbosity = verbosity

    #Deals with debug messages appropriately
    def print(self, message: str, verbosity: int = 0) -> None:
        
        if self.enable and verbosity <= self.verbosity:
            print(message)