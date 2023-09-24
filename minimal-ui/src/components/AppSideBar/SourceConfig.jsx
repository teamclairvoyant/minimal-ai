import { Check } from '@mui/icons-material';
import {
    Button,
    FormControl,
    InputLabel,
    MenuItem,
    Select,
    Stack,
    TextField,
    Typography,
    styled
} from '@mui/material';
import propTypes from 'prop-types';
import { useEffect, useState } from 'react';
import { backendApi } from "../../api/api";
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
    },
    {
        label: 'BIGQUERY',
        value: 'bigquery'
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


const MenuStyle = styled(Stack)({
    maxHeight: 350,
    overflow: 'auto',
    padding: 16,
    gap: 16,
    flexGrow: 1
});

SourceConfig.propTypes = {
    closeBar: propTypes.func,
    currNode: propTypes.any,
    pipelineData: propTypes.object

}

function SourceConfig({ currNode, closeBar, pipelineData }) {
    const [sType, setStype] = useState('')
    const [nodeData, setNodeData] = useState({});

    useEffect(() => {
        console.log(currNode)
        
        const { id } = currNode;
        console.log(pipelineData["tasks"][id])
        if (pipelineData["tasks"] && pipelineData["tasks"]) {
            if (pipelineData["tasks"][id]) {
                const nodeData = pipelineData["tasks"][id] || {}
                setNodeData(nodeData);
                if (nodeData.hasOwnProperty("loader_type")) {
                    if (/local_file|gcp_bucket|aws_s3/.test(nodeData["loader_type"]))
                    setStype("file")
                    else {
                        setStype(nodeData["loader_type"] || "")
                    }
                }
            }
        }
    }, [])

    return (
        <Stack spacing={2}>
            <Typography variant='caption'>Select the Type of Data Source</Typography>
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
            <Stack gap={2}>
                {
                    sType === 'file' && 
                    <FileConfig closeBar={closeBar} currNode={currNode} data={nodeData} pipelineUuid={pipelineData.uuid}/>
                }
                {
                    sType === 'rdbms' && 
                    <RdbmsConfig closeBar={closeBar} currNode={currNode} data={nodeData} pipelineUuid={pipelineData.uuid}/>
                }
                {
                    sType === 'bigquery' && 
                    <BigqueryConfig closeBar={closeBar} currNode={currNode} data={nodeData} pipelineUuid={pipelineData.uuid}/>
                }
            </Stack>
        </Stack>
    )

}

export default SourceConfig


//--------------------------------------------------------------
const ActionButtons = ({ handleSubmit, closeBar }) => {
    return <Stack direction={'row'} justifyContent={"space-between"}>
        <Stack>
        </Stack>
        <Stack direction={'row'} gap={5}>
            <Button variant="text" onClick={closeBar}>
                Cancel
            </Button>
            <Button
                variant="contained"
                size='large'
                color='primary'
                onClick={handleSubmit}
                disableElevation
                startIcon={<Check />}
            >
                Save
            </Button>
        </Stack>
    </Stack>
}

ActionButtons.propTypes = {
    handleSubmit: propTypes.func,
    closeBar: propTypes.func
}
//--------------------------------------------------------------

const FileConfig = ({ closeBar, currNode, data, pipelineUuid }) => {

    const [fileArea, setFileArea] = useState(data?.loader_type || '')
    const [fileType, setFileType] = useState(data?.loader_config?.file_type || '')
    const [filePath, setFilePath] = useState(data?.loader_config?.file_path || '')
    const [, { setPipeline }] = pipelineStore()

    async function handleSubmit() {
        let task_id = currNode.id
        const payload = {
            "config_type": fileArea,
            "config_properties": {
                "file_type": fileType,
                "file_path": filePath
            }
        }
        const response = await backendApi.put(`/pipeline/${pipelineUuid}/task/${task_id}`, payload)

        setPipeline(response.data.pipeline)
        closeBar()
    }

    return (
        <>
            <MenuStyle>
                <FormControl fullWidth variant='standard'>
                    <InputLabel id="select-file-area">File Area</InputLabel>
                    <Select
                        label="File Area"
                        variant='standard'
                        labelId="select-file-area"
                        value={fileArea}
                        required
                        onChange={e => setFileArea(e.target.value)}
                    >
                        {FileArea.map(option => <MenuItem value={option.value} key={option.key}>
                            {option.label}
                        </MenuItem>)}
                    </Select>
                </FormControl>
                <FormControl fullWidth variant='standard' placeholder='Please select the type of the file'>
                    <InputLabel id="select-file-type">File Type</InputLabel>
                    <Select
                        label="File Type"
                        variant='standard'
                        labelId="select-file-type"
                        placeholder='Please select the type of the file'
                        aria-description='Please select the type of the file'
                        value={fileType}
                        required
                        onChange={e => setFileType(e.target.value)}
                    >
                        {FileType.map(option => <MenuItem value={option.value} key={option.key}>
                            {option.label}
                        </MenuItem>)}
                    </Select>
                </FormControl>
                <TextField
                    variant='standard'
                    label='File Path'
                    onChange={e => setFilePath(e.target.value)}
                    value={filePath}
                    helperText="Enter the path of the file"
                    required
                />
            </MenuStyle>
            <ActionButtons
                closeBar={closeBar}
                handleSubmit={handleSubmit}
            />
        </>
    )
}

FileConfig.propTypes = {
    closeBar: propTypes.func,
    currNode: propTypes.any,
    data: propTypes.object,
    pipelineUuid: propTypes.string
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

const RdbmsConfig = ({ closeBar, currNode, data, pipelineUuid }) => {

    const [dbType, setDbType] = useState(data?.loader_config?.db_type || '')
    const [host, setHost] = useState(data?.loader_config?.host || '')
    const [port, setPort] = useState(data?.loader_config?.port || '')
    const [user, setUser] = useState(data?.loader_config?.user || '')
    const [password, setPassword] = useState(data?.loader_config?.password || '')
    const [database, setDatabase] = useState(data?.loader_config?.database || '')
    const [table, setTable] = useState(data?.loader_config?.table || '')
    const [, { setPipeline }] = pipelineStore()

    async function handleSubmit() {

        let task_id = currNode.id
        let payload = {
            "config_type": "rdbms",
            "config_properties": {
                "db_type": dbType,
                "host": host,
                "port": port,
                "user": user,
                "password": password,
                "database": database,
                "table": table
            }
        }

        const response = await backendApi.put(`/pipeline/${pipelineUuid}/task/${task_id}`, payload)

        setPipeline(response.data.pipeline)
        closeBar()
    }

    return (
        <>
            <MenuStyle>
                <FormControl fullWidth variant='standard' required>
                    <InputLabel id="select-file-area">Database Type</InputLabel>
                    <Select
                        label="Database Type"
                        variant='standard'
                        labelId="select-file-area"
                        placeholder='Please select Database Type'
                        value={dbType}
                        required
                        onChange={e => setDbType(e.target.value)}
                    >
                        {RdbmsType.map(option => <MenuItem value={option.value} key={option.key}>
                            {option.label}
                        </MenuItem>)}
                    </Select>
                </FormControl>
                <TextField
                    id="source-host-name"
                    variant='standard'
                    label="Host"
                    value={host}
                    helperText="Enter the host name of the database server"
                    required
                    onChange={e => setHost(e.target.value)}
                />
                <TextField
                    id="source-port-name"
                    variant='standard'
                    label="Port"
                    type='number'
                    placeholder='Please enter port number'
                    helperText="Enter the port number for the database server"
                    onChange={e => setPort(e.target.value)}
                    value={port}
                    required
                />
                <TextField
                    id="source-user-name"
                    variant='standard'
                    label="Username"
                    placeholder='Please enter database username'
                    helperText="Enter the username for the database"
                    onChange={e => setUser(e.target.value)}
                    required
                    value={user}
                />
                <TextField
                    id="source-password-name"
                    variant='standard'
                    label="Password"
                    type='password'
                    placeholder='Please enter database password'
                    onChange={e => setPassword(e.target.value)}
                    value={password}
                    helperText="Enter the password for the database"
                    required
                />
                <TextField
                    id="source-database-name"
                    variant='standard'
                    label="Database"
                    placeholder='Please enter database'
                    onChange={e => setDatabase(e.target.value)}
                    value={database}
                    helperText="Enter the name of the database"
                    required
                />
                <TextField
                    id="source-table-name"
                    variant='standard'
                    label="Table"
                    placeholder='Please enter database'
                    onChange={e => setTable(e.target.value)}
                    value={table}
                    helperText="Enter the name of the database table"
                    required
                />
            </MenuStyle>

            <ActionButtons
                closeBar={closeBar}
                handleSubmit={handleSubmit}
            />
        </>
    )
}


RdbmsConfig.propTypes = {
    closeBar: propTypes.func,
    currNode: propTypes.any,
    data: propTypes.object,
    pipelineUuid: propTypes.string
}

//----------------------------------------------------------------

const BigqueryConfig = ({ closeBar, currNode, data, pipelineUuid }) => {

    const [table, setTable] = useState(data?.loader_config?.table || '')
    const [, { setPipeline }] = pipelineStore()

    async function handleSubmit() {

        let task_id = currNode.id
        let payload = {
            "config_type": "bigquery",
            "config_properties": {
                "table": table
            }
        }

        const response = await backendApi.put(`/pipeline/${pipelineUuid}/task/${task_id}`, payload)

        setPipeline(response.data.pipeline)
        closeBar()
    }

    return (
        <>
            <MenuStyle>
            <TextField
                    id="source-table-name"
                    variant='standard'
                    label="Table"
                    placeholder='Please enter database'
                    onChange={e => setTable(e.target.value)}
                    value={table}
                    helperText="Table format - project-id:dataset:table"
                    required
                />
            </MenuStyle>
            <ActionButtons
                closeBar={closeBar}
                handleSubmit={handleSubmit}
            />
        </>
    )

}

BigqueryConfig.propTypes = {
    closeBar: propTypes.func,
    currNode: propTypes.any,
    data: propTypes.object,
    pipelineUuid: propTypes.string
}