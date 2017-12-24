import csv, sys

suburbs_to_include = set()
suburbs_included = set()

with open('Syd_Suburbs.csv') as suburbs_file:
    suburbs_csv = csv.reader(suburbs_file)
    for suburb_row in suburbs_csv:
        suburb = suburb_row[0].strip('\ufeff')
        if suburb != "NSW SUBURB":
            suburbs_to_include.add(suburb)


print("%d suburbs to include" % (len(suburbs_to_include)), file = sys.stderr)

input_filename = "Census2016_Bedrooms_Persons_NoChildren_OwnerOccupied_NSW_Suburbs-output.csv"
output_filename = input_filename.split('.')[0] + "-geofiltered.csv"

input_file = open(input_filename, "r")
output_file = open(output_filename, "w")
output_writer = csv.writer(output_file)

isHeader = True

for input_row in csv.reader(input_file):
    suburb = input_row[0].upper()

    if isHeader:
        output_writer.writerow(input_row)
        isHeader = False

    # e.g. Gowrie (Singleton - NSW) -> Gowrie
    suburb = suburb.split('(')[0].strip()

    if suburb in suburbs_to_include:
        suburbs_included.add(suburb)
        output_writer.writerow(input_row)

not_included = suburbs_to_include.difference(suburbs_included)

if len(not_included) > 0:
    print("WARNING: suburbs for inclusion but not included: ", not_included, file=sys.stderr)
