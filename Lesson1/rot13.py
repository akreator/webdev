def encodeText(str):
    str = list(str)
    str = [encodeLetter(char) for char in str];
    return ''.join(str)
    
def encodeLetter(char):
    if char.isalpha():
        val = ord(char) + 13
        if val > 122 or 90 < val <= 103:
            val -= 26       
        return chr(val)
    return char
        
print encodeText("Hello there!  What's your name?")
 