import sys
"""
Code to convert .asm assembly file to .hack binary file
"""
class Parser:

	"""
	it takes file pointer of assembly language file as input
	and returns a list containing sequence of code
	"""
	@staticmethod
	def __clean(fp):
		list_of_commands = []
		for line in fp:
			line = line.strip()
			if len(line) == 0:
				continue
			elif line[0] == "/":
				continue
			else:
				line = line.split()
				list_of_commands.append(line[0])
		return list_of_commands

	@staticmethod
	def parse(fp):
		codeWriter_lines = Parser.__clean(fp)
		list_of_commands = []
		for line in codeWriter_lines:
			if line[0] == "@":
				list_of_commands.append(("A-instruction", line[1:]))
			elif line[0] == "(":
				list_of_commands.append(("label", line[1:line.find(")")].strip()))
			else:
				temp_dict = {}
				if line.find("=") != -1:
					temp_dict["dist"] = line[:line.find("=")]
					line = line[line.find("=")+1:]
				if line.find(";") == -1:
					temp_dict["comp"] = line
				else:
					temp_dict["comp"] = line[:line.find(";")]
					temp_dict["jump"] = line[line.find(";")+1:]
				list_of_commands.append(("C-instruction", temp_dict))

		return list_of_commands


class SymbolTable(object):
	"""docstring for SymbolTable"""
	def __init__(self):
		self.map = {"SP":0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4,
					"SCREEN": 16384, "KBD": 24576}
		for i in range(16):
			self.map["R" + str(i)] = i

	def check(self, label):
		if label in self.map:
			return True
		else:
			return False

	def get(self, label):
		if label in self.map:
			return self.map[label]
		else:
			return None

	def insert(self, label, value):
		# you can insert only once
		# this will provide immutability
		if label not in self.map:
			self.map[label] = value

	def first_pass(self, list_of_commands):
		address = 0
		for command in list_of_commands:
			if command[0] == "label" and command[1] not in self.map:
				self.map[command[1]] = address
			elif command[0] != "label":
				address += 1



class CodeWriter(object):
	"""docstring for CodeWriter"""
	comp_map, dist_map, jump_map = {}, {}, {}
	dist_map["M"] = "001"
	dist_map["D"] = "010"
	dist_map["MD"] = "011"
	dist_map["A"] = "100"
	dist_map["AM"] = "101"
	dist_map["AD"] = "110"
	dist_map["AMD"] = "111"

	jump_map["JGT"] = "001"
	jump_map["JEQ"] = "010"
	jump_map["JGE"] = "011"
	jump_map["JLT"] = "100"
	jump_map["JNE"] = "101"
	jump_map["JLE"] = "110"
	jump_map["JMP"] = "111"

	comp_map["0"] = "0101010"
	comp_map["1"] = "0111111"
	comp_map["-1"] = "0111010"
	comp_map["D"] = "0001100"
	comp_map["A"] = "0110000"
	comp_map["!D"] = "0001101"
	comp_map["!A"] = "0110001"
	comp_map["-D"] = "0001111"
	comp_map["-A"] = "0110011"
	comp_map["D+1"] = "0011111"
	comp_map["A+1"] = "0110111"
	comp_map["D-1"] = "0001110"
	comp_map["A-1"] = "0110010"
	comp_map["D+A"] = "0000010"
	comp_map["D-A"] = "0010011"
	comp_map["A-D"] = "0000111"
	comp_map["D&A"] = "0000000"
	comp_map["D|A"] = "0010101"

	comp_map["M"] = "1110000"
	comp_map["!M"] = "1110001"
	comp_map["-M"] = "1110011"
	comp_map["M+1"] = "1110111"
	comp_map["M-1"] = "1110010"
	comp_map["D+M"] = "1000010"
	comp_map["D-M"] = "1010011"
	comp_map["M-D"] = "1000111"
	comp_map["D&M"] = "1000000"
	comp_map["D|M"] = "1010101"

	@staticmethod
	def convert(list_of_commands, symbol_table):
		comp_map = CodeWriter.comp_map
		dist_map = CodeWriter.dist_map
		jump_map = CodeWriter.jump_map

		final_codeWriter = []
		address = 16
		for command in list_of_commands:
			if command[0] == "A-instruction":
				if command[1].isnumeric():
					final_codeWriter.append(bin(int(command[1])).replace('0b',''))
				elif symbol_table.check(command[1]):
					num = int(symbol_table.get(command[1]))
					final_codeWriter.append(bin(num).replace('0b',''))
				else:
					symbol_table.insert(command[1], address)
					final_codeWriter.append(bin(address).replace('0b',''))
					address += 1

			elif command[0] == "C-instruction":
				binary_command = "111"
				binary_command += comp_map[command[1]["comp"]]
				if "dist" in command[1]:
					binary_command += dist_map[command[1]["dist"]]
				else:
					binary_command += "000"
				
				if "jump" in command[1]:
					binary_command += jump_map[command[1]["jump"]]
				else:
					binary_command += "000"
				final_codeWriter.append(binary_command)

		return final_codeWriter
		

def main():
	try:
		file_name = sys.argv[1]
	except Exception as e:
		print("File Name Unavailable! Please Enter One.")
		return
	if file_name.rfind(".") == -1 or file_name[file_name.rfind("."):] != ".asm":
		print("Invalid File Extension! Please Enter .asm File")
		return
	try:
		fp = open(file_name)
	except Exception as e:
		print("File Not Found! Please Enter Another.")
		return
	list_of_commands = Parser.parse(fp)

	symbol_table = SymbolTable()
	symbol_table.first_pass(list_of_commands)
	final_codeWriter = CodeWriter.convert(list_of_commands, symbol_table)
	output_fp = open(file_name[:file_name.rfind(".")] + ".hack", "w")
	for line in final_codeWriter:
		line = "0"*(16-len(line)) + line
		output_fp.write(line + "\n")
	output_fp.close()

if __name__ == '__main__':
	main()