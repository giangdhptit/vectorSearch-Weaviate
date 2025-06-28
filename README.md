Brief summary of my work & the errors that I got & how I fixed them.

1. Issues in virtualenv -> reinstalled the packages, downgraded python version
2. Missing some critical files from Weaviate package -> go with another approach using different packages.
3. Many many issues while trying to connect with weaviate
   -> I downgraded the weaviate client, upgraded again, changed the syntax to connect. I ended up with the latest version: 4.15
4. Errors for schema/table creation (it was because weaviate has changed the naming convention, now it is called "collections" instead;
   the syntax to get the model is also changed)
   -> Fixed by switching to the new syntax of weaviate client 4.x.x
5. Errors in importing data to weaviate
   -> print out logs to check for issues
   -> change the syntax for data importing

For weaviate connection, all the features from v3 is now deprecated 
-> Will never work even if we change the syntax/ try with different effort.
v4 syntax is totally different from v3, and in this case, ChatGPT can't figure it out 
-> We have to go to official document from weaviate to check for new syntax
