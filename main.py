#import gzip

#with gzip.open('all_articles_originalv2.json.gz', 'rt', encoding='utf-8') as f:
#    for line in f:
#        print(line)

# Now, data contains the JSON object from the file
#print(data)
#import csv
#import os
# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


#def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    #print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

#def convert_json_to_csv(json_filepath, csv_filepath):
    # Load JSON data from the file
#    try:
#        with open(json_filepath, 'r', encoding='utf-8') as json_file:
 #           articles = json.load(json_file)
#    except Exception as e:
        #print(f"Failed to load JSON file {json_filepath}: {e}")
#        return

    # Write data to a CSV file
 #   try:
  #      with open(csv_filepath, 'w', newline='', encoding='utf-8') as csvfile:
            # Assuming that the JSON contains a list of dictionaries with consistent keys
   #         fieldnames = articles[0].keys()  # Use the keys of the first article as the header
    #        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
     #       writer.writeheader()
      #      for article in articles:
       #         writer.writerow(article)
        #print(f"Successfully converted {json_filepath} to {csv_filepath}")
#    except Exception as e:
 #       print(f"Failed to write to CSV file {csv_filepath}: {e}")

# Example usage
#json_filename = 'data/articles_2024_08.json'  # Replace with your actual JSON file path
#csv_filename = 'data/articles_2024_08.csv'    # Replace with your desired CSV file path


# Press the green button in the gutter to run the script.
#if __name__ == '__main__':
 #   print_hi('PyCharm')
  #  convert_json_to_csv(json_filename, csv_filename)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/



