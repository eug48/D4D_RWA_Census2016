
# coding: utf-8

# In[109]:


"""
parses Australian Bureau of Statistics TableBuilder "CSV" exports

e.g.
Australian Bureau of Statistics

"2016 Census - Selected Dwelling Characteristics"
"SSC by BEDRD Number of Bedrooms in Private Dwelling (ranges) by NPRD Number of Persons Usually Resident in Dwelling"
"Counting: Dwellings, Location on Census Night"

Filters:
"Default Summation","Dwellings, Location on Census Night"

" Aarons Pass"
"NPRD Number of Persons Usually Resident in Dwelling","Five persons","Four persons","Three persons","Two persons","One person","Total",
"BEDRD Number of Bedrooms in Private Dwelling (ranges)",
"Two bedrooms",0,0,0,0,0,0,
"Three bedrooms",0,0,0,0,3,4,
"Four bedrooms",0,0,0,0,0,0,
"Five bedrooms",0,0,0,0,0,0,
"Six bedrooms or more",0,0,0,0,0,0,
"Total",0,0,0,0,3,8,


" Abbotsbury"
"NPRD Number of Persons Usually Resident in Dwelling","Five persons","Four persons","Three persons","Two persons","One person","Total",
"BEDRD Number of Bedrooms in Private Dwelling (ranges)",
"Two bedrooms",0,0,5,0,3,10,
"Three bedrooms",11,54,42,58,32,198,
"Four bedrooms",116,234,154,166,51,721,
"Five bedrooms",42,50,28,18,3,145,
"Six bedrooms or more",10,5,0,0,0,16,
"Total",175,338,228,249,86,1081,
"""
def read_wafers(f, axisNames):
    prevLine = None
    
    def remove_quotes(s):
        return s.strip().strip('"').strip()
    
    wafer = None
    colNames = None
    for rawLine in f:
        line = rawLine.rstrip()
        #print(line)
        if line.startswith('"' + axisNames[0] + ' '):
            # description of column axis
            colNames = list(map(remove_quotes, line.split(',')[1:]))
            title = remove_quotes(prevLine)
            wafer = { "title": title, "lineNum": 0}
        
        if wafer != None:
            if line == "":
                # wafers seem to always end with a blank line
                del wafer["lineNum"]
                yield wafer
                wafer = None
                colNames = None

            elif wafer["lineNum"] >= len(axisNames): # skip past axis descriptions
                fields = line.rstrip(',').split(',')
                rowName = remove_quotes(fields[0])
                values = fields[1:]

                valuesDict = dict([ [colNames[i], int(v)] for i, v in enumerate(values)])
                wafer[rowName] = valuesDict

            if wafer != None:
                wafer["lineNum"] += 1
        prevLine = line

def calc_underoccupied_rooms(wafer):
    def count(rowName, *colNames):
        row = wafer[rowName]
        values = [ row[col] for col in colNames ]
        return sum(values)
        
    bedrooms = {
        2: count("Two bedrooms", "One person"),
        3: count("Three bedrooms", "One person", "Two persons"),
        4: count("Four bedrooms", "One person", "Two persons", "Three persons"),
        5: count("Five bedrooms", "One person", "Two persons", "Three persons", "Four persons"),
        6: count("Six bedrooms or more", "One person", "Two persons", "Three persons", "Four persons", "Five persons"),
    }
    total = sum(bedrooms.values())
    return total


# In[119]:


columnNames = ["NPRD", "BEDRD"]
input_filename = "Census2016_Bedrooms_Persons_NSW_LGA.csv"
input_filename = "Census2016_Bedrooms_Persons_NSW_Suburbs.csv"
output_filename = input_filename.replace(".csv","") + "-output.csv"

import csv

with open(input_filename) as f, open(output_filename,'w') as o:
    writer = csv.writer(o)
    #writer.writerow(['lga_name_2014','Underoccupied rooms'])
    writer.writerow(['Suburb','Underoccupied rooms'])
    
    wafers = read_wafers(f, columnNames)
    #wafers = list(wafers)[1:2]
    for wafer in wafers:
        title = wafer["title"]
        row = title, calc_underoccupied_rooms(wafer)
        #print(*row, sep='')
        if title != 'Total':
            writer.writerow(row)

