from effects import ask    
    
    
def riddle_1()    
    """On the poster is a riddle"""
    answer = ask("""[italic]"I HAVE KEYS BUT I CAN'T OPEN A SINGLE LOCK. WHAT AM I?"[/]""")
    if "keyboard" in answer.lower() or "piano" in answer.lower():
        say('The screen goes dark.[pause] Behind the cabinet, something clicks.')
        return True