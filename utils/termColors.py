import colored
from colored import stylize, fg, bg, attr

class TermColors:
    testvar        = "Testvar" 
    infoHead       = fg("white") + bg("blue") + attr("bold")
    warnHead       = fg("white") + bg("yellow") + attr("bold")
    successHead    = fg("white") + bg("green") + attr("bold")
    dangerHead     = fg("white") + bg("red") + attr("bold")

    info           = fg("blue") 
    warn           = fg("yellow") 
    success        = fg("green") 
    danger         = fg("red")

    def test():
        infoHead       = fg("white") + bg("blue") + attr("bold")
        warnHead       = fg("white") + bg("yellow") + attr("bold")
        successHead    = fg("white") + bg("green") + attr("bold")
        dangerHead     = fg("white") + bg("red") + attr("bold")

        info           = fg("blue") 
        warn           = fg("yellow") 
        success        = fg("green") 
        danger         = fg("red")
        styles = [  infoHead, 
                    info, 
                    warnHead,
                    warn,
                    successHead,
                    success,
                    dangerHead,
                    danger ]
        
        for style in styles:
            print(stylize("Test", style))


if __name__ == "__main__":
    TermColors.test()
    print(stylize("New", TermColors.infoHead))
        