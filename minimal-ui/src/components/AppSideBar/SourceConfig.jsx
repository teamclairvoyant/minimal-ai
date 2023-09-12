import propTypes from 'prop-types'
import { Typography,
    styled,
    MenuItem, 
    TextField,
    Stack,
    Fab} from '@mui/material'
import { useState } from 'react'
import SaveIcon from '@mui/icons-material/Save';
import CloseIcon from '@mui/icons-material/Close';
import { backendApi } from "../../api/api"
import { pipelineStore } from "../../appState/pipelineStore";
// -------------------------------------------------------

const sourceType = [
    {
        label: 'File',
        value: 'file'
    },
    {
        label: 'RDBMS',
        value: 'rdbms'
    }
]

const FileType = [
    {
        label: 'CSV',
        value: 'csv'
    },
    {
        label: 'JSON',
        value: 'json'
    },
    {
        label: 'PARQUET',
        value: 'parquet'
    }
]

const FileArea = [
    {
        label: 'LOCAL',
        value: 'local_file'
    },
    {
        label: 'GCP BUCKET',
        value: 'gcp_bucket'
    },
    {
        label: 'AWS S3',
        value: 'aws_s3'
    }
]


const MenuStyle = styled('div')({
    display: 'flex',
    flexDirection:'row',
    flexWrap: 'wrap',
    alignItems: 'center', 
    justifyContent:'space-between',
    marginLeft:20
});

SourceConfig.propTypes = {
    closeBar: propTypes.func,
    currNode: propTypes.any

}

function SourceConfig({currNode, closeBar}) {
    const [ sType, setStype ] = useState('')
    

    return (
        <MenuStyle>
            <div>
                <Stack spacing={2} direction="row" sx={{marginBottom: 4,justifyContent:'space-around', alignItems: 'center'}}>
                    <Typography sx={{ mb: 5 }}>Source</Typography>
                    <TextField
                        select
                        onChange={(event) => (setStype(event.target.value))}
                        value={sType}
                        helperText="Please select data source"
                        required
                        sx={{width:220}}
                    >
                        {sourceType.map((option) => (
                            <MenuItem key={option.value} value={option.value}>
                            {option.label}
                            </MenuItem>
                        ))}
                    </TextField>
                </Stack>
                { sType === 'file' && <FileConfig closeBar={closeBar} currNode={currNode}></FileConfig>}
                { sType === 'rdbms' && <RdbmsConfig closeBar={closeBar} currNode={currNode}></RdbmsConfig>}
            </div>
        </MenuStyle>
    )

}

export default SourceConfig

//--------------------------------------------------------------

const FileConfig = ({closeBar, currNode}) => {
    const [fileArea, setFileArea] = useState('')
    const [fileType, setFileType] = useState('')
    const [filePath, setFilePath] = useState('')
    const [bucketName, setBucketName] = useState('')
    const [showBucketField, setShowBucketField] = useState(false)
    const [{pipeline},{setPipeline}] = pipelineStore()


    async function handleSubmit() {

        let task_id = currNode.id
        let payload = {
            "config_type" : fileArea,
            "config_properties" : {
                "file_type": fileType,
                "file_path": filePath
            } 
        }
        const response = await backendApi.put(`/api/v1/pipeline/${pipeline.uuid}/task/${task_id}`,payload)

        setPipeline(response.data.pipeline)
        closeBar()
    }

    const areaChange = (event) => {
        setShowBucketField(false)
        if (event.target.value === 'gcp_bucket' || event.target.value === 'aws_s3' ){
            setShowBucketField(true)
        }
        setFileArea(event.target.value);
      };
 
    return (
        <MenuStyle>
            <div>
                <Stack spacing={2} direction="row" sx={{marginBottom: 4,justifyContent:'space-around', alignItems: 'center'}}>
                    <Typography sx={{ mb: 5 }}>File Area</Typography>
                    <TextField
                        select
                        onChange={areaChange}
                        value={fileArea}
                        helperText="Please select file area"
                        required
                        sx={{width:220}}
                    >
                        {FileArea.map((option) => (
                            <MenuItem key={option.value} value={option.value}>
                            {option.label}
                            </MenuItem>
                        ))}
                    </TextField>
                </Stack>
                {showBucketField && (
                    <Stack spacing={2} direction="row" sx={{marginBottom: 4, alignItems: 'center'}}>
                        <Typography>Bucket Name</Typography>
                        <TextField
                        type='text'
                        variant='outlined'
                        onChange={e => setBucketName(e.target.value)}
                        value={bucketName}
                        fullWidth
                        helperText="Please enter bucket name"
                        />
                    </Stack>
                )}
                <Stack spacing={2} direction="row" sx={{marginBottom: 4,justifyContent:'space-around', alignItems: 'center'}}>
                    <Typography sx={{ mb: 5 }}>File Type</Typography>
                    <TextField
                        select
                        onChange={e => setFileType(e.target.value)}
                        value={fileType}
                        helperText="Please select file type"
                        required
                        sx={{width:220}}
                    >
                        {FileType.map((option) => (
                            <MenuItem key={option.value} value={option.value}>
                            {option.label}
                            </MenuItem>
                        ))}
                    </TextField>
                </Stack>
                <Stack spacing={2} direction="row" sx={{marginBottom: 4,justifyContent:'space-around', alignItems: 'center'}}>
                    <Typography>File Path</Typography>
                    <TextField
                    type='text'
                    variant='outlined'
                    onChange={e => setFilePath(e.target.value)}
                    value={filePath}
                    helperText="Please enter file path"
                    required
                    sx={{width:220}}
                    />
                </Stack>


                
                <div id='button-menu' style={{display:'flex',flexDirection:'row', justifyContent:'space-around', paddingTop:'20px'}}>
                    <Fab variant="extended" color="error" onClick={closeBar}>
                        <CloseIcon sx={{ mr: 1 }} />
                        Cancel
                    </Fab>
                    <Fab variant="extended" color="primary" onClick={handleSubmit}>
                        <SaveIcon sx={{ mr: 1 }} />
                        Save
                    </Fab>
                </div>
            </div>
     
        </MenuStyle>
    )
}

FileConfig.propTypes = {
    closeBar: propTypes.func,
    currNode: propTypes.any
}

//---------------------------------------------------------------------

const RdbmsType = [
    {
        label: 'MYSQL',
        value: 'mysql'
    },
    {
        label: 'POSTGRESSQL',
        value: 'postgressql'
    }
]

const RdbmsConfig = ({closeBar, currNode}) => {
    const [dbType, setDbType] = useState('')
    const [host, setHost] = useState('')
    const [port, setPort] = useState('')
    const [user, setUser] = useState('')
    const [password, setPassword] = useState(false)
    const [database, setDatabase] = useState('')
    const [table, setTable] = useState('')
    const [{pipeline}, {setPipeline}] = pipelineStore()

    async function handleSubmit() {

        let task_id = currNode.id
        let payload = {
            "config_type" : "rdbms",
            "config_properties" : {
                "db_type": dbType,
                "host": host,
                "port": port,
                "user": user,
                "password": password,
                "database": database,
                "table": table
            } 
        }

        const response = await backendApi.put(`/api/v1/pipeline/${pipeline.uuid}/task/${task_id}`,payload)

        setPipeline(response.data.pipeline)
        closeBar()
    }

    return (
        <MenuStyle>
            <div>
                <Stack spacing={2} direction="row" sx={{marginBottom: 4,justifyContent:'space-around', alignItems: 'center'}}>
                    <Typography sx={{ mb: 5 }}>DB Type</Typography>
                    <TextField
                        select
                        onChange={e => setDbType(e.target.value)}
                        value={dbType}
                        helperText="Please select DB type"
                        required
                        sx={{width:220}}
                    >
                        {RdbmsType.map((option) => (
                            <MenuItem key={option.value} value={option.value}>
                            {option.label}
                            </MenuItem>
                        ))}
                    </TextField>
                </Stack>
                <Stack spacing={2} direction="row" sx={{marginBottom: 4,justifyContent:'space-around', alignItems: 'center'}}>
                    <Typography>Host</Typography>
                    <TextField
                    type='text'
                    variant='outlined'
                    onChange={e => setHost(e.target.value)}
                    value={host}
                    helperText="Please enter host name"
                    required
                    sx={{width:220}}
                    />
                </Stack>
                <Stack spacing={2} direction="row" sx={{marginBottom: 4,justifyContent:'space-around', alignItems: 'center'}}>
                    <Typography>Port</Typography>
                    <TextField
                    type='text'
                    variant='outlined'
                    onChange={e => setPort(e.target.value)}
                    value={port}
                    helperText="Please enter port number"
                    required
                    sx={{width:220}}
                    />
                </Stack>
                <Stack spacing={2} direction="row" sx={{marginBottom: 4,justifyContent:'space-around', alignItems: 'center'}}>
                    <Typography>User</Typography>
                    <TextField
                    type='text'
                    variant='outlined'
                    onChange={e => setUser(e.target.value)}
                    value={user}
                    helperText="Please enter user"
                    required
                    sx={{width:220}}
                    />
                </Stack>
                <Stack spacing={2} direction="row" sx={{marginBottom: 4,justifyContent:'space-around', alignItems: 'center'}}>
                    <Typography>Password</Typography>
                    <TextField
                    type='password'
                    variant='outlined'
                    onChange={e => setPassword(e.target.value)}
                    value={password}
                    helperText="Please enter password"
                    required
                    sx={{width:220}}
                    />
                </Stack>
                <Stack spacing={2} direction="row" sx={{marginBottom: 4,justifyContent:'space-around', alignItems: 'center'}}>
                    <Typography>Database</Typography>
                    <TextField
                    type='text'
                    variant='outlined'
                    onChange={e => setDatabase(e.target.value)}
                    value={database}
                    helperText="Please enter database"
                    required
                    sx={{width:220}}
                    />
                </Stack>
                <Stack spacing={2} direction="row" sx={{marginBottom: 4,justifyContent:'space-around', alignItems: 'center'}}>
                    <Typography>Table</Typography>
                    <TextField
                    type='text'
                    variant='outlined'
                    onChange={e => setTable(e.target.value)}
                    value={table}
                    helperText="Please enter table"
                    required
                    sx={{width:220}}
                    />
                </Stack>

                <div id='button-menu' style={{display:'flex',flexDirection:'row', justifyContent:'space-around', paddingTop:'20px'}}>
                    <Fab variant="extended" color="error" onClick={closeBar}>
                        <CloseIcon sx={{ mr: 1 }} />
                        Cancel
                    </Fab>
                    <Fab variant="extended" color="primary" onClick={handleSubmit}>
                        <SaveIcon sx={{ mr: 1 }} />
                        Save
                    </Fab>
                </div>
            </div>
        </MenuStyle>
    )
}

RdbmsConfig.propTypes = {
    closeBar: propTypes.func,
    currNode: propTypes.any
}