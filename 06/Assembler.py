import sys
import os
address_marker = 16 #for variable storage
comp_table = {
    "0": "0101010",
    "1": "0111111",
    "-1": "0111010",
    "D": "0001100",
    "A": "0110000",
    "!D": "0001101",
    "!A": "0110001",
    "-D": "0001111",
    "-A": "0110011",
    "D+1": "0011111",
    "A+1": "0110111",
    "D-1": "0001110",
    "A-1": "0110010",
    "D+A": "0000010",
    "D-A": "0010011",
    "A-D": "0000111",
    "D&A": "0000000",
    "D|A": "0010101",
    "M": "1110000",
    "!M": "1110001",
    "-M": "1110011",
    "M+1": "1110111",
    "M-1": "1110010",
    "D+M": "1000010",
    "D-M": "1010011",
    "M-D": "1000111",
    "D&M": "1000000",
    "D|M": "1010101"
    }


dest_table = {
    "null": "000",
    "M": "001",
    "D": "010",
    "A": "100",
    "MD": "011",
    "AM": "101",
    "AD": "110",
    "AMD": "111"
    }


jmp_table = {
    "null": "000",
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111"
    }

table = {
    "SP": 0,
    "LCL": 1,
    "ARG": 2,
    "THIS": 3,
    "THAT": 4,
    "SCREEN": 16384,
    "KBD": 24576,
    }

for i in range(0,16):
  label = "R" + str(i)
  table[label] = i
	
def parse(line):	#recursively strip the lines
	char = line[0]
	if char == "\n" or char == "/":
		return ""
	elif char == " ":
		return parse(line[1:])
	else:
		return char + parse(line[1:])


def translate(line):
	print(line)
	if line[0]=="@":
		return atranslate(line)
	else:
		return ctranslate(line)

def add_variable(label):
	#add a variable to symbol table
	global address_marker
	table[label] = address_marker
	address_marker += 1
	return table[label]	


def atranslate(line):
	if line[1].isalpha():
		label = line[1:]	#check if label
		a_value = table.get(label,-1)
		if a_value == -1:	#add to the table if not already existed
			a_value = add_variable(label)
	else:
		a_value = int(line[1:])
	return bin((a_value))[2:].zfill(16) #since bin returns ob001100 etc 

def ctranslate(line):
	#separate into three parts cmp dst and jmp
	#first, make every line has the same format
	if not "=" in line:
		line = "null=" + line
	if not ";" in line:
		line = line +";null"
	temp = line.split("=")
	destbin = dest_table.get(temp[0], "Destination error")
	temp = temp[1].split(";")
	compbin = comp_table.get(temp[0], "Computation error")
	jmpbin = jmp_table.get(temp[1], "Jump Error")
	return "111" + compbin + destbin + jmpbin

def add_labels():
	#add the labels with their following line number
	asm_file = sys.argv[1]
	first_pass_file = open(asm_file[:-4] + ".tmp" , "w")
	with open(asm_file, "r+") as asm_instructions:
		line_number = 0	
		for line in asm_instructions:
			parsed_line = parse(line)
			if parsed_line != "":
				if parsed_line[0] == "(":
					label = parsed_line[1:-1]
					table[label] = line_number
					parsed_line = ""
				else:
					line_number += 1
					first_pass_file.write(parsed_line + "\n")
	first_pass_file.close()

def assemble():
	asm_file = sys.argv[1]
	hack_instructions = open(asm_file[:-4]+".hack", "w")
	with open(asm_file[:-4] + ".tmp", "r") as asm_instructions:
		for line in asm_instructions:
			line = parse(line)
			binary_line = translate(line)
			hack_instructions.write(binary_line + "\n")
	hack_instructions.close()
	os.remove(asm_file[:-4] + ".tmp")
add_labels()
assemble()
print(table)
