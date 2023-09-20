import SaveIcon from '@mui/icons-material/Save';
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
import { useState } from 'react';
import { backendApi } from "../../api/api";
import { pipelineStore } from "../../appState/pipelineStore";
// -------------------------------------------------------


const MenuStyle = styled(Stack)({
    maxHeight: 350,
    overflow: 'auto',
    padding: 16,
    gap: 16,
    flexGrow: 1
});

const transformType = [
    {
        label: 'JOIN',
        value: 'join'
    },
    {
        label: 'FILTER',
        value: 'filter'
    }
]

TransformConfig.propTypes = {
    closeBar: propTypes.func,
    currNode: propTypes.any
}
function TransformConfig({closeBar,currNode}) {
    const [ transType,setTransType ] = useState('')

  return (

    <Stack spacing={2}>
        <Typography variant='caption'>Select the Type Transformation</Typography>
        <TextField
            select
            onChange={(event) => (setTransType(event.target.value))}
            value={transType}
            helperText="Transformation Type"
            required
            sx={{width:220}}
        >
            {transformType.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                {option.label}
                </MenuItem>
            ))}
        </TextField>
        <Stack gap={2}>
            { transType === 'join' && <JoinConfig closeBar={closeBar} currNode={currNode}/>}
            { transType === 'filter' && <FilterConfig closeBar={closeBar} currNode={currNode}/>}
        </Stack>
    </Stack>
  )
}

export default TransformConfig

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
                startIcon={<SaveIcon />}
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

//---------------------------------------------------------------

const joinType = [
    {
        label: 'Full Outer Join',
        value: 'full_outer'
    },
    {
        label: 'Left Join',
        value: 'left'
    },
    {
        label: 'Right Join',
        value: 'right'
    },
    {
        label: 'Cross Join',
        value: 'cross'
    },
    {
        label: 'Inner Join',
        value: 'inner'
    }
]

const JoinConfig = ({closeBar,currNode}) => {
    const [how, setHow] = useState('')
    const [leftTable, setLeftTable] = useState('')
    const [rightTable, setRightTable] = useState('')
    const [leftOn, setLeftOn] = useState('')
    const [rightOn, setRightOn] = useState('')
    const [{pipeline},{setPipeline}] = pipelineStore()

    async function handleSubmit() {

        let task_id = currNode.id
        let payload = {
            "config_type" : 'join',
            "config_properties" : {
                "left_table": leftTable,
                "right_table": rightTable,
                "left_on": [leftOn],
                "right_on": [rightOn],
                "how": how
            } 
        }
        const response = await backendApi.put(`/pipeline/${pipeline.uuid}/task/${task_id}`,payload)

        setPipeline(response.data.pipeline)
        closeBar()
    }
    
    return(
        <>
            <MenuStyle>
                <FormControl fullWidth variant='standard' placeholder='Please select the type of the file'>
                    <InputLabel id="select-file-type">Join Type</InputLabel>
                    <Select
                        label="Join Type"
                        variant='standard'
                        labelId="select-join-type"
                        helperText="Please select the type of the Join"
                        placeholder='Please select the type of the Join'
                        aria-description='Please select the type of the Join'
                        value={how}
                        required
                        onChange={e => setHow(e.target.value)}
                    >
                        {joinType.map(option => <MenuItem value={option.value} key={option.key}>
                            {option.label}
                        </MenuItem>)}
                    </Select>
                </FormControl>
                <TextField
                    variant='standard'
                    label='Left Table'
                    onChange={e => setLeftTable(e.target.value)}
                    value={leftTable}
                    helperText="Enter the name of left table"
                    required
                />
                
                <TextField
                    variant='standard'
                    label='Right Table'
                    onChange={e => setRightTable(e.target.value)}
                    value={rightTable}
                    helperText="Enter the name of right table"
                    required
                />
                <TextField
                    variant='standard'
                    label='Left On Condition'
                    onChange={e => setLeftOn(e.target.value)}
                    value={leftOn}
                    helperText="Enter the join condition"
                    required
                />
                <TextField
                    variant='standard'
                    label='Right On Condition'
                    onChange={e => setRightOn(e.target.value)}
                    value={rightOn}
                    helperText="Enter the join condition"
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

JoinConfig.propTypes = {
    closeBar : propTypes.func,
    currNode: propTypes.any
}

//---------------------------------------------------------------

const FilterConfig = ({closeBar,currNode}) => {
    const [filter,setFilter] = useState('')
    const [{pipeline},{setPipeline}] = pipelineStore()
    async function handleSubmit() {

        let task_id = currNode.id
        let payload = {
            "config_type" : 'filter',
            "config_properties" : {
                "filter": filter
            } 
        }
        const response = await backendApi.put(`/pipeline/${pipeline.uuid}/task/${task_id}`,payload)

        setPipeline(response.data.pipeline)
        closeBar()
    }

    return(
        <>
            <MenuStyle>
            <TextField
                    variant='standard'
                    label='Filter Clause'
                    onChange={e => setFilter(e.target.value)}
                    value={filter}
                    helperText="Enter the join condition"
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

FilterConfig.propTypes = {
    closeBar : propTypes.func,
    currNode: propTypes.any
}