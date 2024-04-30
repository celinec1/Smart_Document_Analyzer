# ## secure file uploader

# ## create folder for the files 
# def createFolder(username, name):
#     if username in username_database:
#         if folder not in file_database:
#             file_database.append(folder)
#             return "success"
#     return "failed"


# ## authenticate the file, making sure it's an accepted form (pdf)
# def authenticateFile(username, file):
#     if username in username_database:
#         if folder in file_database:
#             if ".pdf" in file:
#                 return "success"
#             else:
#                 return "file type invalid"

# ## successfully upload the authenticated file into folder
# def uploadFile(username, folder, file):
#     if username in username_database:
#         if folder in file_database:
#             if authenticateFile(file) == "success":
#                 file_database.append(file)
#                 return "success upload"
#     return "failed upload"

# ## the fileInfo would save the date, location of the file, make changes to the name 
# def fileInfo(username, file):
#     if file in file_database:
#         fileInfo_map= {}
#         fileInfo_map[date] = fileInfo.date()
#         fileInfo_map[storage] = fileInfo.size()
#         fileInfo_map[location] = fileInfo.folder()
#         fileInfo_map[username] = fileInfo.username()

# ## delete the file
# def deleteFile(username, file):
#     if file in file_database:
#         delete(file)
#         return "deleted succesfully"
#     return "unsuccessful delete"


