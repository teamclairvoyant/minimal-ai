import { useState } from 'react';
import { Button, Dialog, DialogContent, TextField, DialogActions, Stack } from '@mui/material';
import propTypes from "prop-types"
import Iconify from './Iconify';


AppMenu.propTypes = {
    menuName: propTypes.string,
    type: propTypes.string,
    iconName: propTypes.string,
    buttonColor: propTypes.string,
    addNode: propTypes.func
}


function ShowTaskModal(openModal, setOpenModal, type, addNode) {
    const [taskName, setTaskName] = useState('')

    return (
        <div>
            <Dialog open={openModal} onClose={() => setOpenModal(false)}>
                <DialogContent>
                    <TextField margin="dense" id="task-name" onChange={(e) => setTaskName(e.target.value)} label="Task Name" type="text" fullWidth variant="standard" />
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setOpenModal(false)}>Cancel</Button>
                    <Button onClick={() => {
                        addNode(type, taskName)
                        setOpenModal(false)
                    }}
                    >
                        Create
                    </Button>
                </DialogActions>
            </Dialog>
        </div>
    )
}


// function SourceMenu(menuName,addNode,setAnchorEl){
//     const [open, setOpen] = useState(false)
//     const [taskType, setTaskType] = useState('')

//     function openTaskModal(sType){
//         setOpen(true)
//         setTaskType(sType)
//     }

//     if (menuName == "Source"){
//         return (
//             <div>
//                 <div>
//                     <MenuItem onClick={() => openTaskModal("file")}>File</MenuItem>
//                     <MenuItem onClick={() => openTaskModal("rdbms")}>Rdbms</MenuItem>
//                 </div>
//                 {ShowTaskModal(open, setOpen,'input',taskType,addNode,setAnchorEl)}
//             </div>
//         )
//     }
//     else if (menuName == "Transform") {
//         return (
//             <div>
//                 <div>
//                     <MenuItem onClick={() => openTaskModal("join")}>Join</MenuItem>
//                     <MenuItem onClick={() => openTaskModal("transform")}>Filter</MenuItem>
//                     <MenuItem onClick={() => openTaskModal("transform")}>Group By</MenuItem>
//                     <MenuItem onClick={() => openTaskModal("transform")}>Rename Column</MenuItem>
//                 </div>
//                 {ShowTaskModal(open, setOpen,'default',taskType,addNode,setAnchorEl)}
//             </div>
//         )
//     }
//     else {
//         return (
//             <div>
//                 <div>
//                     <MenuItem onClick={() => openTaskModal("file")}>File</MenuItem>
//                     <MenuItem onClick={() => openTaskModal("rdbms")}>Data Warehouse</MenuItem>
//                 </div>
//                 {ShowTaskModal(open, setOpen,'output',taskType,addNode,setAnchorEl)}
//             </div>
//         )
//     }
// }


export default function AppMenu({ menuName, type, iconName, buttonColor, addNode }) {

    const [open, setOpen] = useState(false)

    return (
        <Stack>
            <Button variant="contained" color='secondary' onClick={() => setOpen(true)}
                startIcon={<Iconify icon={iconName} />}
            >
                {menuName}
            </Button>
            {ShowTaskModal(open, setOpen, type, addNode)}
        </Stack>
    );
}
