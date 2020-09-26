import sys
import os 

class Parser(object):
    def __init__(self,filename):
        self.vmfile = open(filename)
        self.vmcommand = ["None"]
        self.reachedEOF = False
        self.commandType = {
                "sub" : "C_ARITHMETIC",
                "add" : "C_ARITHMETIC",
                "neg" : "C_ARITHMETIC",
                "eq" : "C_ARITHMETIC",
                "gt" : "C_ARITHMETIC",
                "lt" : "C_ARITHMETIC",
                "and" : "C_ARITHMETIC",
                "or" : "C_ARITHMETIC",
                "not" : "C_ARITHMETIC",
                "push" : "C_PUSH",
                "pop" : "C_POP"
                }

    def advance(self):
       # check if current line is a comment, if not, parse the command into
       # lexical components
        currentLine = self.vmfile.readline()
        if currentLine == "":
            self.reachedEOF = True
        else:
            splitLine = currentLine.split("/")[0].strip()
            if splitLine == "":
                #it means the current line is a comment 
                self.advance()
            else:
                self.vmcommand = splitLine.split()
                #vmcommand is a list of words

    def moreCommands(self):
        #check if the file pointer reached EOF 
        file_pointer_position = self.vmfile.tell()
        #since advance function moves the file pointer we save and restore the
        #pointer
        self.advance()
        self.vmfile.seek(file_pointer_position)
        return not self.reachedEOF

    def CommandType(self):
        #return the comment type according to the dictionary
        return self.commandType.get(self.vmcommand[0], "Error Ctype")
    
    def arg1(self):
        return self.vmcommand[1]

    def arg2(self):
        return self.vmcommand[2]
    
class CodeWriter:
    def __init__(self, filename):
        self.asmfile = open(filename[:-3] + ".asm", "w")
        self.without_extension = filename[:-3] 
        self.label = 0 #this is for logical operations
        self.segment = {
                "local" : "LCL",
                "argument" : "ARG",
                "this" : "THIS",
                "that" : "THAT",
                "temp" : "5",
                "pointer" : "3"
                }
    
    def operand1(self):
        #pop first operand from stack
        return_string = ""
        return_string += "@SP\n"
        return_string += "AM=M-1\n"
        return_string += "D=M\n"
        return return_string
    
    def operand2(self):
        #pop second operand from stack
        return_string = ""
        return_string += "@SP\n"
        return_string += "A=M-1\n"
        return return_string
    def arith_function(self,code):
        #do the operation and put it back on the stack
        return_string = ""
        label = str(self.label)
        self.label += 1
        if code == "add":
            return_string += "M=D+M\n"
        elif code == "sub":
            return_string += "M=M-D\n"
        elif code == "neg":
            return_string += "M=-M\n"
        elif code == "and":
            return_string += "M=D&M\n"
        elif code == "or":
            return_string += "M=D|M\n"
        elif code == "not":
            return_string += "M=!M\n"
        #for logical operations it is a little bit tricky
        elif code == "gt":
            return_string += "D=M-D\n" 
            return_string += "@gt"+label+"\n"
            return_string += "D;JGT\n"
            return_string += "M=0\n"
            return_string += "(gt"+label+")\n"
            return_string += "M=-1\n" 
        elif code == "lt":
            return_string += "D=M-D\n" 
            return_string += "@lt"+label+"\n"
            return_string += "D;JLT\n"
            return_string += "M=0\n"
            return_string += "(lt"+label+")\n"
            return_string += "M=-1\n" 
        elif code == "eq":
            return_string += "D=M-D\n" 
            return_string += "@eq"+label+"\n"
            return_string += "D;JEQ\n"
            return_string += "M=0\n"
            return_string += "(eq"+label+")\n"
            return_string += "M=-1\n" 
        return return_string
    
    def write(self, translation):
        self.asmfile.write(translation)
    
    def writeArithmetic(self, vmcommand):
        if vmcommand == "add":
            self.write(self.operand1() + self.operand2() + self.arith_function("add"))
        elif vmcommand == "sub":
            self.write(self.operand1() + self.operand2() + self.arith_function("sub"))
        elif vmcommand == "neg":
            self.write(self.operand2() + self.arith_function("neg"))
        elif vmcommand == "and":
            self.write(self.operand1() + self.operand2() + self.arith_function("and"))
        elif vmcommand == "or":
            self.write(self.operand1() + self.operand2() + self.arith_function("or"))
        elif vmcommand == "not":
            self.write(self.operand2() + self.arith_function("not"))
        elif vmcommand == "gt":
            self.write(self.operand1() + self.operand2() + self.arith_function("gt"))
        elif vmcommand == "lt":
            self.write(self.operand1() + self.operand2() + self.arith_function("lt"))
        elif vmcommand == "eq":
            self.write(self.operand1() + self.operand2() + self.arith_function("eq"))
    
    def extract_segment(self, segment, i):
        if segment in ("local", "argument", "this", "that"):
            return_string = "@" + i + "\nD=A\n@" + self.segment.get(segment) + "\nA=M+D\nD=M\n"
        else:
            return_string = "@" + i + "\nD=A\n@5\nA=A+D\nD=M\n"
        return return_string

    def pushD(self):
        return_string = "@SP\nA=M\nM=D\n"
        return return_string

    def incre_SP(self):
        return_string = "@SP\nM=M+1\n"
        return return_string

    def const_to_D(self, i):
        return_string = "@" + i + "\nD=A\n"
        return return_string
    
    def static_to_D(self, i):
        return_string = "@" + self.without_extension + "." + i + "\nD=M\n"
        return return_string

    def pointer_to_D(self, i):
        return_string = "@"+ i + "\nD=A\n@3\nA=D+A\nD=M\n"
        return return_string
    
    def pop_to_D(self):
        return_string = "@SP\nAM=M-1\nD=M\n"
        return return_string

    def D_to_mem(self):
        return_string = "@R13\nA=M\nM=D\n"
        return return_string
    
    def D_to_static(self , i):
        return_string = "@" + self.without_extension + "." + i + "\nM=D\n"
        return return_string


    def add_to_reg(self, segment, i):
        if segment in ("local", "argument", "this", "that" ):
            return_string = "@"+ i +"\nD=A\n@"+ self.segment.get(segment) + "\nD=M+D\n@R13\nM=D\n"
        elif segment in ("temp", "pointer"):
            return_string =  "@"+ i +"\nD=A\n@"+ self.segment.get(segment) + "\nD=A+D\n@R13\nM=D\n"
        return return_string

    

    def write_push(self, segment, i): 
        if segment in ("local", "argument", "this", "that"):
            self.write(self.extract_segment(segment,i) + self.pushD() + self.incre_SP())
        elif segment == "constant":
            self.write(self.const_to_D(i) + self.pushD() + self.incre_SP())
        elif segment == "static":
            self.write(self.static_to_D(i) + self.pushD() + self.incre_SP())
        elif segment == "temp":
            self.write(self.extract_segment(segment, i) + self.pushD() + self.incre_SP())
        elif segment == "pointer":
            self.write(self.pointer_to_D(i) + self.pushD() + self.incre_SP())

    def write_pop(self, segment, i):
        if segment in ("local", "argument", "this", "that", "temp", "pointer"):
            self.write(self.add_to_reg(segment, i) + self.pop_to_D() + self.D_to_mem())
        elif segment == "static":
            self.write(self.pop_to_D() + self.D_to_static(i))
    
def main():
    filename = sys.argv[1]
    parser = Parser(filename)
    writer = CodeWriter(filename)
    while parser.moreCommands():
        command_string = " ".join([str(word) for word in parser.vmcommand]) + "\n"
        writer.write("//" + command_string)
        if parser.CommandType() == "C_ARITHMETIC":
            writer.writeArithmetic(parser.vmcommand[0])
        elif parser.CommandType() == "C_PUSH":
            writer.write_push(parser.arg1(), parser.arg2())
        elif parser.CommandType() == "C_POP":
            writer.write_pop(parser.arg1(), parser.arg2())
        parser.advance()
if __name__ == "__main__":
    main()
            
    
    
            
        
        

        

