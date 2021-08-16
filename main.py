import os, itertools
import cv2
import numpy as np
import time

file_list = []

start = time.process_time()

for file in os.walk('./'):
    path = file[0]
    # Remove the extra / if root folder to avoid './/'
    if (path == "./"):
        path = "."
    for name in file[2]:
        filepath = f"{path}/{name}"
        if cv2.haveImageReader(filepath):
            file_list.append((filepath, cv2.imread(filepath)))

print(f"Images scanned: {len(file_list)} in {(time.process_time() - start):.4f}s.")
duplicate_list = {}
# Restart timer
start = time.process_time()

for file1, file2 in itertools.combinations(file_list, 2):
    print(f"Comparing {file1[0]} and {file2[0]} - ", end = '')
    if file1[1].size != file2[1].size:
        print("Images are different.")
        continue;

    diff = cv2.absdiff(file1[1],file2[1])
    result = np.any(diff)

    if result:
        # ΔE range from 0 to 100 - 0 is identical, 100 is exactly opposite
        # Difference is calculated by ΔE of all pixels divided by number of pixels
        # Referenced from https://en.wikipedia.org/wiki/Color_difference
        # Convert BGR into CIELAB colour space to use CIE76 colour difference formula
        file1_cvt = cv2.cvtColor(file1[1],cv2.COLOR_BGR2LAB) 
        file2_cvt = cv2.cvtColor(file2[1],cv2.COLOR_BGR2LAB)

        # Compute difference
        delta_E = cv2.absdiff(file1_cvt,file2_cvt)
        delta_L, delta_a, delta_b = cv2.split(delta_E)
        sum_delta_e = np.mean(np.sqrt(cv2.multiply(delta_L, delta_L) + cv2.multiply(delta_a, delta_a) + cv2.multiply(delta_b, delta_b)))
        print(f"Images have a delta E of {(sum_delta_e):.4f}.")
    else:
        print("Images are the same.")
        # Notes: 
        # Itertools Combinations generates pairs as [a,b,c] = [a,b], [a,c], [b,c]
        # 1st Case: file1 not in dup list (therefore file2 also not in list) -> file1 key, file2 in list value
        # 2nd Case: file1 in dup list, file2 not -> extend file2 in list value
        # 3rd Case: file1 & file2 in dup list (because earlier file0 added both) -> do nothing

        inserted = False
        for dups in duplicate_list:
            # Case 2/3 if file1 is key.
            if dups == file1[0]:
                duplicate_list[file1[0]].add(file2[0])
                inserted = True
                break
            for dup in duplicate_list[dups]:
                # Case 2/3 if file1 is value.
                if dup == file1[0]: 
                    duplicate_list[dups].add(file2[0])
                    inserted = True
                    break
            # Method of breaking out of the double loop.
            if inserted:
                break
        # Case 1.
        if not inserted:
            duplicate_list[file1[0]] = {file2[0]}

print(f"\nTime taken to compare images: {(time.process_time() - start):.4f}s.")
print(f"Duplicates:")
dup_count = 0
for dups in duplicate_list:
    print(f"[{dups}", end = '')
    for dup in duplicate_list[dups]:
        print(f", {dup}", end = '')
        dup_count += 1
    print("]")
print(f"Duplicate Count: {dup_count}")

# If no duplicates detected, exit program.
response = None
if dup_count == 0:
    response = 3

while response is None:
    try:
        response = int(input("\n1. Remove duplicates on a step-by-step review process.\n2. Remove all duplicates without reviewing based off date created.\n3. Exit.\nSelect an option: "))
        if response not in (1, 2, 3):
            raise ValueError
    except ValueError:
        print(f"{response} is not a valid response. Please try again.")
        response = None
    
if response == 1:
    for dups in duplicate_list:
        # For each duplicate tuple in the list, gather all relevant information and present to the user so they can manually review
        dup_info = [(dups, time.ctime(os.path.getctime(dups)), time.ctime(os.path.getmtime(dups)))]
        for dup in duplicate_list[dups]:
            dup_ctime = time.ctime(os.path.getctime(dup))
            dup_mtime = time.ctime(os.path.getmtime(dup))
            dup_info.append((dup, dup_ctime, dup_mtime))
        
        # Present information of duplicates
        print()
        for idx, dup in enumerate(dup_info):
            print(f"{idx+1}. File: {dup[0]}, Date Created: {dup[1]}, Date Modified: {dup[2]}")

        # Provide decision of which photo to keep
        keep = None
        while keep is None:
            try:
                keep = int(input("Select an image to keep: "))
                if keep <= 0 or keep > len(dup_info):
                    raise ValueError
                # Ensure keep matches the image index
                keep -= 1
            except ValueError:
                print(f"{keep} is not a valid response. Please try again.\n")
                keep = None

        # Remove all duplicates except selected
        for idx, dup in enumerate(dup_info):
            if idx == keep:
                continue
            try:
                os.remove(dup[0])
                print(f"Deleted {dup[0]}")
            except OSError as e:
                print(f"Error: {dup[0]} - {e}")


    print("\nFinished. You should now check for empty folders.")

if response == 2:
    for dups in duplicate_list:
        date_created = (dups, time.ctime(os.path.getctime(dups)))
        for dup in duplicate_list[dups]:
            dup_time = time.ctime(os.path.getctime(dup))
            # Update the earliest file if current image has an earlier created time.
            if dup_time < date_created[1]:
                try:
                    os.remove(date_created[0])
                    print(f"Deleted {date_created[0]}")
                except OSError as e:
                    print(f"Error: {date_created[0]} - {e}")
                date_created = (dup, dup_time)
            else:
                try:
                    os.remove(dup)
                    print(f"Deleted {dup}")
                except OSError as e:
                    print(f"Error: {dup} - {e}")
    print("Finished. You should now check for empty folders.")

print("Exiting.")