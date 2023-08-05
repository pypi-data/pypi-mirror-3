"""The modul "inputhandler" has a function  dinput, that let you specify which kind of datatyp you need as userinput and will print a string
until your requirements (with additional dataranges) are fullfilled."""

def dinput(output = 'Please enter an integer: ', sinput = 'Illegal input, try again.',
           datatyp = int, ranges = False, lowerlimit = 0, upperlimit = 100, rsinput = "Integer does not lie between 0, 100: " ):
        """With output you specify the inputprompt.
        With sinput you specify the errormessage for wrong datatyp-input
        With datayp you specify which kind of datatyp you require(int, double ...)
        With ranges = True, you can specify lowerlimit and upperlimit in which the uservalue should lie
        and with rsinput you have a special erromessage if the value lies not in the required range."""
        try:
                if(ranges):
                        userinput = input(output)
                        a = datatyp(userinput)
                        if(lowerlimit <= a <=upperlimit):
                                return a
                        else:
                                print(rsinput)
                                a = dinput(output, sinput, datatyp,
                                           ranges, lowerlimit,
                                           upperlimit, rsinput)
                                return a
                else:
                    userinput = input(output)
                    return(datatyp(userinput))
        except:
                print(sinput)
                a = dinput(output, sinput, datatyp,
                           ranges, lowerlimit,
                           upperlimit, rsinput)
                return a
