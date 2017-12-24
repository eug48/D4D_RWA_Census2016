"""
parses Australian Bureau of Statistics TableBuilder "CSV" exports
"""
def read_wafers(f, axisNames):
    
    def remove_quotes(s):
        return s.strip().strip('"').strip()
    
    rowLabels = axisNames[1]
    fullKeyFields = None
    colLabelsPrefix = ','*(len(rowLabels) - 1) + '"' + axisNames[0] + ' '
    colLabels = None
    prevLine = None
    wafer = None

    for rawLine in f:
        line = rawLine.rstrip()
        #print(line)
        if line.startswith(colLabelsPrefix):
            # description of column axis
            colLabels = list(map(remove_quotes, line.split(',')[len(rowLabels):]))
            title = remove_quotes(prevLine)
            wafer = { "title": title, "lineNum": 0}
        
        if wafer != None:
            if line == "": # wafers seem to always end with a blank line
                del wafer["lineNum"]
                yield wafer
                wafer = None
                colLabels = None

            elif wafer["lineNum"] >= len(axisNames): # skip past axis descriptions
                fields = list(map(remove_quotes, line.rstrip(',').split(',')))

                keyFields = fields[0:len(rowLabels)]
                keyFields = [ s if len(s) > 0 else fullKeyFields[i] for (i,s) in enumerate(keyFields)]
                fullKeyFields = keyFields

                values = fields[len(rowLabels):]
                valuesDict = dict([ [colLabels[i], int(v)] for i, v in enumerate(values)])
                wafer[tuple(keyFields)] = valuesDict

            if wafer != None:
                wafer["lineNum"] += 1
        prevLine = line

def calc_underoccupied_rooms(wafer):
    def count(wantedLabel1, *colLabels):
        values = []

        for ( keyFields , row) in wafer.items():
            if keyFields[0] == wantedLabel1:
                rowValues = [ row[col] for col in colLabels ]
                values.extend(rowValues)

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



import csv

axesLabels = ["NPRD", ("BEDRD","HCFMD","TEND")  ]
input_filename = "Census2016_Bedrooms_Persons_NoChildren_OwnerOccupied_NSW_Suburbs.csv"
output_filename = input_filename.replace(".csv","") + "-output.csv"


with open(input_filename) as f, open(output_filename,'w') as o:
    writer = csv.writer(o)
    #writer.writerow(['lga_name_2014','Underoccupied rooms'])
    writer.writerow(['Suburb','Underoccupied rooms'])
    
    wafers = read_wafers(f, axesLabels)
    #wafers = list(wafers)[1:2]
    for wafer in wafers:
        #print(wafer)
        title = wafer["title"]
        row = title, calc_underoccupied_rooms(wafer)
        #print(*row, sep='')
        if title != 'Total':
            writer.writerow(row)

