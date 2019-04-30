# cuckoo-report-parser
A python project to help read Cuckoo Sandbox report files.

Cuckoo report files can be very large and in my recent research I used the code in this repository to parse Cuckoo report files.
I found that attempting to load the files into memory failed and I wasn't able to find a decent Python stream parser for JSON.
Instead, my strategy was to first index certain JSON blocks in the report files and then use those indexes to seek to 
specific file locations and then only read parts of the files into memory.

## index-reports.py

This repository contains three sample JSON report files, zipped for convenience.  index-reports.py unzips each of the samples 
and creates an index file for each.  For my purposes I have indexed the following sections of a report.

| Report Section | Section Start to Index      |
| -------------- |-----------------------------|
| Strings        | '    \"strings\": ['        |
| Target         | '    \"target\": {'         |
| API Statistics | '        \"apistats\": {'   |
| Processes      | '        \"processes\": ['  |
| Imports        | '        \"pe_imports\": [' |

Index files end .idx and are named the same as their corresponding report file.  An example index file is shown below.  
The values relate to the file locations of the start and end of the relevant JSON sections in the file.

### Sample Index File

```json
{
  "strings": {"start": 136714613, "end": 136733985}, 
  "target": {"start": 33503, "end": 34344}, 
  "apistats": {"start": 5076540, "end": 5094593}, 
  "processes": {"start": 5094596, "end": 133675814}, 
  "imports": {"start": 538560, "end": 550915}
}
```

## read-reports.py

read-reports.py reads each indexed section of a report file, using the file seek data stored in the index file.  To allow easy
understanding of the output, only ten elements from each section are printed to the console. 

### Example Output
```bash
md5: 1934bc240ae9e8e101490a9dab13c079 strings: !This program cannot be run in DOS mode.	`.data	.rdata	@.pdata	@.idata	WWWWWS	...
Imports md5: 1934bc240ae9e8e101490a9dab13c079 dll: advapi32.dll import: RegCloseKey
Imports md5: 1934bc240ae9e8e101490a9dab13c079 dll: advapi32.dll import: RegQueryValueExA
Imports md5: 1934bc240ae9e8e101490a9dab13c079 dll: advapi32.dll import: RegSetValueExA
Imports md5: 1934bc240ae9e8e101490a9dab13c079 dll: advapi32.dll import: RegDeleteValueA
Imports md5: 1934bc240ae9e8e101490a9dab13c079 dll: advapi32.dll import: RegOpenKeyExA
Imports md5: 1934bc240ae9e8e101490a9dab13c079 dll: user32.dll import: SetWindowTextA
Imports md5: 1934bc240ae9e8e101490a9dab13c079 dll: user32.dll import: PostQuitMessage
Imports md5: 1934bc240ae9e8e101490a9dab13c079 dll: user32.dll import: DispatchMessageA
Imports md5: 1934bc240ae9e8e101490a9dab13c079 dll: user32.dll import: UpdateWindow
Imports md5: 1934bc240ae9e8e101490a9dab13c079 dll: user32.dll import: CreateWindowExA
Imports md5: 1934bc240ae9e8e101490a9dab13c079 dll: user32.dll import: SetWindowPos
Calls md5: 1934bc240ae9e8e101490a9dab13c079 api: ldrgetdllhandle time: 1540552603.953375
Calls md5: 1934bc240ae9e8e101490a9dab13c079 api: ldrgetprocedureaddress time: 1540552603.953375
Calls md5: 1934bc240ae9e8e101490a9dab13c079 api: ldrgetprocedureaddress time: 1540552603.953375
Calls md5: 1934bc240ae9e8e101490a9dab13c079 api: ldrgetprocedureaddress time: 1540552603.953375
Calls md5: 1934bc240ae9e8e101490a9dab13c079 api: getusernamew time: 1540552603.953375
Calls md5: 1934bc240ae9e8e101490a9dab13c079 api: ldrgetdllhandle time: 1540552603.953375
Calls md5: 1934bc240ae9e8e101490a9dab13c079 api: ldrgetprocedureaddress time: 1540552603.953375
Calls md5: 1934bc240ae9e8e101490a9dab13c079 api: ntprotectvirtualmemory time: 1540552603.953375
Calls md5: 1934bc240ae9e8e101490a9dab13c079 api: ldrgetprocedureaddress time: 1540552603.953375
Calls md5: 1934bc240ae9e8e101490a9dab13c079 api: ldrgetprocedureaddress time: 1540552603.953375
Calls md5: 1934bc240ae9e8e101490a9dab13c079 api: ntallocatevirtualmemory time: 1540552603.953375
API Stats md5: 1934bc240ae9e8e101490a9dab13c079 call: CreateToolhelp32Snapshot count: 1
API Stats md5: 1934bc240ae9e8e101490a9dab13c079 call: GetNativeSystemInfo count: 6
API Stats md5: 1934bc240ae9e8e101490a9dab13c079 call: DeviceIoControl count: 7
API Stats md5: 1934bc240ae9e8e101490a9dab13c079 call: CoUninitialize count: 1
API Stats md5: 1934bc240ae9e8e101490a9dab13c079 call: RegCloseKey count: 33
API Stats md5: 1934bc240ae9e8e101490a9dab13c079 call: NtDuplicateObject count: 13
API Stats md5: 1934bc240ae9e8e101490a9dab13c079 call: NtSetInformationFile count: 2
API Stats md5: 1934bc240ae9e8e101490a9dab13c079 call: RegQueryValueExA count: 28
API Stats md5: 1934bc240ae9e8e101490a9dab13c079 call: NtCreateKey count: 5
API Stats md5: 1934bc240ae9e8e101490a9dab13c079 call: IsDebuggerPresent count: 7
API Stats md5: 1934bc240ae9e8e101490a9dab13c079 call: GetSystemWindowsDirectoryW count: 7
```