1. Download python 3.6.X and install

2. Download Python_Compiler folder

3. Copy the ai script you are compiling from your standard file into file "AI_Script.ais" as the compiler is set to only compile this file.
You will not compile anything if this step is not completed.

4. Double Click compiler.

5. Done compiling.

6. You will recieve 3 files, the compiled bytes, an offset list of every label in the file and an error page. 
If you have no hex data in your compiled file, check your errors. 

7. Copy the dynamic offset you inputted at the top of your script. ctrl + G in HxD or jump to address in any hex editor.

8. Copy and paste data in the exact location you defined. If you do not do this correctly, you will softlock or crash your rom. 

9. The script table is at offset 1D9BF4. Every 4 bytes is a pointer to 1 script. Check the title of the script you compiled.
Take the script number and multiply it by 4 then minus 4 and add it to the offset provided. This is the pointer you need to change. Point it at the new script.
Ex: You compiled script 2. 2 x 4 = 8 - 4 = 4. 1D9BF4 + 4 = 1D98F8. Go to the new offset and change it to point at the new script.

Notes:
If you cannot understand this, go research about pointers and tables :)
