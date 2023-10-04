import { Check } from '@mui/icons-material';
import {
    Button,
    FormControl,
    FormControlLabel,
    InputLabel,
    MenuItem,
    Radio,
    RadioGroup,
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
    maxHeight: 400,
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
    const [sType, setStype] = useState('');
    const [nodeData, setNodeData] = useState({});

    useEffect(() => {
        const { id } = currNode;
        if (pipelineData["tasks"] && pipelineData["tasks"]) {
            if (pipelineData["tasks"][id]) {
                const nodeData = pipelineData["tasks"][id] || {}
                setNodeData(nodeData);
                if (nodeData.hasOwnProperty("loader_type")) {
                    setStype("file");
                }
            }
        }
    }, []);

    return (
        <Stack spacing={2}>
            <Typography variant='caption'>Select the Type of Data Source</Typography>
            <RadioGroup
                row
                required
                name="source-type-radio-button"
                onChange={e => {
                    setStype(e.target.value);
                }}
                value={sType}
            >
                {sourceType.map(option => <FormControlLabel
                    key={option.label}
                    value={option.value}
                    label={option.label}
                    control={<Radio />}
                />)}
            </RadioGroup>
            <Stack gap={2}>
                {sType === 'file' && <FileConfig closeBar={closeBar} currNode={currNode} data={nodeData}></FileConfig>}
                {sType === 'rdbms' && <RdbmsConfig closeBar={closeBar} currNode={currNode} data={nodeData}></RdbmsConfig>}
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
    closeBar: propTypes.func,
}
//--------------------------------------------------------------

const FileConfig = ({ closeBar, currNode, data }) => {
    const [fileArea, setFileArea] = useState(data?.loader_type || '');
    const [fileType, setFileType] = useState(data?.loader_config?.file_type || '');
    const [filePath, setFilePath] = useState(data?.loader_config?.file_path || '');
    const [bucketName, setBucketName] = useState('')
    const [keyPath, setKeyPath] = useState('')
    const [showBucketField, setShowBucketField] = useState(false)
    const [{ pipeline }, { setPipeline }] = pipelineStore()

    async function handleSubmit() {
        let task_id = currNode.id
        var payload = {}
        if (fileArea === 'gcp_bucket' || fileArea === 'aws_s3')
        {
            payload = {
                "config_type": fileArea,
                "config_properties": {
                    "file_type": fileType,
                    "bucket_name": bucketName,
                    "key_file": keyPath,
                    "file_path": filePath
                }
            }
        }
        else {
            payload = {
                "config_type": fileArea,
                "config_properties": {
                    "file_type": fileType,
                    "file_path": filePath
                }
            }
        }
        const response = await backendApi.put(`/pipeline/${pipeline.uuid}/task/${task_id}`, payload)

        setPipeline(response.data.pipeline)
        closeBar()
    }

    const areaChange = (event) => {
        setShowBucketField(false)
        if (event.target.value === 'gcp_bucket' || event.target.value === 'aws_s3') {
            setShowBucketField(true)
        }
        setFileArea(event.target.value);
    };

    return (
        <>
            <MenuStyle>
                <FormControl fullWidth variant='standard'>
                    <InputLabel id="select-file-area">File Area</InputLabel>
                    <Select
                        label="File Area"
                        variant='standard'
                        labelId="select-file-area"
                        helperText='Select the area where the file is placed'
                        value={fileArea}
                        required
                        onChange={areaChange}
                    >
                        {FileArea.map(option => <MenuItem value={option.value} key={option.key}>
                            {option.label}
                        </MenuItem>)}
                    </Select>
                </FormControl>
                {showBucketField && (
                    <>
                        <TextField
                            id="source-bucket-name"
                            variant='standard'
                            value={bucketName}
                            label="Bucket Name"
                            helperText="Enter the name of the bucket where the file is located"
                            required
                            onChange={e => setBucketName(e.target.value)}
                        />
                        <TextField
                            id="source-key-path"
                            variant='standard'
                            value={keyPath}
                            label="key path"
                            helperText="Enter the path of the service key file"
                            required
                            onChange={e => setKeyPath(e.target.value)}
                        />
                    </>
                )}
                <FormControl fullWidth variant='standard' placeholder='Please select the type of the file'>
                    <InputLabel id="select-file-type">File Type</InputLabel>
                    <Select
                        label="File Type"
                        variant='standard'
                        labelId="select-file-type"
                        helperText="Please select the type of the file"
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
    data: propTypes.object
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

const RdbmsConfig = ({ closeBar, currNode, data }) => {
    console.log(data);
    const [dbType, setDbType] = useState('')
    const [host, setHost] = useState('')
    const [port, setPort] = useState('')
    const [user, setUser] = useState('')
    const [password, setPassword] = useState('')
    const [database, setDatabase] = useState('')
    const [table, setTable] = useState('')
    const [{ pipeline }, { setPipeline }] = pipelineStore()

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

        const response = await backendApi.put(`/pipeline/${pipeline.uuid}/task/${task_id}`, payload)

        setPipeline(response.data.pipeline)
        closeBar()
    }

    return (
        <>
                <FormControl fullWidth variant='standard' required>
                    <InputLabel id="select-file-area">Database Type</InputLabel>
                    <Select
                        label="Database Type"
                        variant='standard'
                        labelId="select-file-area"
                        placeholder='Please select Database Type'
                        helperText="Please select Database Type"
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
                    helperText="Enter the host name or IP address of the database server"
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
    data: propTypes.object
}