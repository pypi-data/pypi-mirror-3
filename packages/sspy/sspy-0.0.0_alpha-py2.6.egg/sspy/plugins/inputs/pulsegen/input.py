


class Input:

    def __init__(self):

        pass



    def Format(self):
        
        """
        @brief Prints the text block format that is parsed for the input
        """
        return self._plugin_data.GetFormat()
    
    
    def Add(self, input=None, options=None):

        pass

    def Advance(self, options=None):

        pass

    def Step(self, options=None):
        """
        @brief An alias for the advance method.
        @sa Advance
        
        """
        self.Advance(options)

    def Connect(self):

        pass

    def Finish(self):

        pass

    def Initiate(self):

        pass

    def New(self):

        pass

    def Step(self):

        pass

    def GetCore(self):

        pass
