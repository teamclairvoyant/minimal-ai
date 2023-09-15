import CloseIcon from '@mui/icons-material/Close';
import SaveIcon from '@mui/icons-material/Save';
import {
    Fab,
    MenuItem,
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


const MenuStyle = styled('div')({
    display: 'flex',
    flexDirection:'row',
    flexWrap: 'wrap',
    alignItems: 'center', 
    justifyContent:'space-between',
    marginLeft:20
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
    <MenuStyle>
            <div>
                <Stack spacing={2} direction="row" sx={{marginBottom: 4,justifyContent:'space-around', alignItems: 'center'}}>
                    <Typography sx={{ mb: 5 }}>Type</Typography>
                    <TextField
                        select
                        onChange={(event) => (setTransType(event.target.value))}
                        value={transType}
                        helperText="Please select data source"
                        required
                        sx={{width:220}}
                    >
                        {transformType.map((option) => (
                            <MenuItem key={option.value} value={option.value}>
                            {option.label}
                            </MenuItem>
                        ))}
                    </TextField>
                </Stack>
                { transType === 'join' && <JoinConfig closeBar={closeBar} currNode={currNode}/>}
                { transType === 'filter' && <FilterConfig closeBar={closeBar} currNode={currNode}/>}
            </div>
        </MenuStyle>
  )
}

export default TransformConfig

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
        <MenuStyle>
            <div>
                <Stack spacing={2} direction="row" sx={{marginBottom: 4,justifyContent:'space-around', alignItems: 'center'}}>
                    <Typography sx={{ mb: 5 }}>Join Type</Typography>
                    <TextField
                        select
                        onChange={e => setHow(e.target.value)}
                        value={how}
                        helperText="Please select Join type"
                        required
                        sx={{width:220}}
                    >
                        {joinType.map((option) => (
                            <MenuItem key={option.value} value={option.value}>
                            {option.label}
                            </MenuItem>
                        ))}
                    </TextField>
                </Stack>
                <Stack spacing={2} direction="row" sx={{marginBottom: 4,justifyContent:'space-around', alignItems: 'center'}}>
                    <Typography>Left Table</Typography>
                    <TextField
                    type='text'
                    variant='outlined'
                    onChange={e => setLeftTable(e.target.value)}
                    value={leftTable}
                    helperText="Please enter file path"
                    required
                    sx={{width:220}}
                    />
                </Stack>
                <Stack spacing={2} direction="row" sx={{marginBottom: 4,justifyContent:'space-around', alignItems: 'center'}}>
                    <Typography>Right Table</Typography>
                    <TextField
                    type='text'
                    variant='outlined'
                    onChange={e => setRightTable(e.target.value)}
                    value={rightTable}
                    helperText="Please enter file path"
                    required
                    sx={{width:220}}
                    />
                </Stack>
                <Stack spacing={2} direction="row" sx={{marginBottom: 4,justifyContent:'space-around', alignItems: 'center'}}>
                    <Typography>Left On</Typography>
                    <TextField
                    type='text'
                    variant='outlined'
                    onChange={e => setLeftOn(e.target.value)}
                    value={leftOn}
                    helperText="Please enter file path"
                    required
                    sx={{width:220}}
                    />
                </Stack>
                <Stack spacing={2} direction="row" sx={{marginBottom: 4,justifyContent:'space-around', alignItems: 'center'}}>
                    <Typography>Right on</Typography>
                    <TextField
                    type='text'
                    variant='outlined'
                    onChange={e => setRightOn(e.target.value)}
                    value={rightOn}
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
        <MenuStyle>
            <div>
                <Stack spacing={2} direction="row" sx={{marginBottom: 4,justifyContent:'space-around', alignItems: 'center'}}>
                    <Typography>Filter Clause</Typography>
                    <TextField
                    type='text'
                    variant='outlined'
                    onChange={e => setFilter(e.target.value)}
                    value={filter}
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

FilterConfig.propTypes = {
    closeBar : propTypes.func,
    currNode: propTypes.any
}