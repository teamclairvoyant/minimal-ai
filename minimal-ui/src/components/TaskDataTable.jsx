import CloseIcon from '@mui/icons-material/Close';
import Dialog from '@mui/material/Dialog';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import IconButton from '@mui/material/IconButton';
import { styled } from '@mui/material/styles';
import { DataGrid } from '@mui/x-data-grid';
import propTypes from "prop-types";
import { useEffect, useState } from 'react';
import { backendApi } from '../api/api';
import { pipelineStore } from '../appState/pipelineStore';

const BootstrapDialog = styled(Dialog)(({ theme }) => ({
  '& .MuiDialogContent-root': {
    padding: theme.spacing(2),
  },
  '& .MuiDialogActions-root': {
    padding: theme.spacing(1),
  },
}));

DataDialogs.propTypes = {
    open: propTypes.bool,
    setOpen: propTypes.func,
    task: propTypes.string
}

export default function DataDialogs({open,setOpen, task}) {
    const [{pipeline},] = pipelineStore()
    const [ sampleRecords,setSampleRecords ] = useState(null)

    useEffect(() => {
        async function getTaskData() {
            const response = await backendApi.get(`/sample_data?pipeline_uuid=${pipeline.uuid}&task_uuid=${task}`);
            // console.log(response.data)
            setSampleRecords(response.data);
          }
          getTaskData();
    }, [])
    if (sampleRecords){ 

    return (
        <div>
        <BootstrapDialog
            onClose={() => setOpen(false)}
            aria-labelledby="customized-dialog-title"
            open={open}
        >
            <DialogTitle sx={{ m: 0, p: 2 }} id="customized-dialog-title">
            Sample data
            </DialogTitle>
            <IconButton
            aria-label="close"
            onClick={() => setOpen(false)}
            sx={{
                position: 'absolute',
                right: 8,
                top: 8,
                color: (theme) => theme.palette.grey[500],
            }}
            >
            <CloseIcon />
            </IconButton>
            <DialogContent dividers>
            <DataTable data={sampleRecords}/>
            </DialogContent>
        </BootstrapDialog>
        </div>
    )}
}


DataTable.propTypes = {
    data: propTypes.object
}
function DataTable({data}) {

    function uuidv4() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'
        .replace(/[xy]/g, function (c) {
            const r = Math.random() * 16 | 0, 
                v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }

    function modifyColumn(columns){
        return columns.map(obj => ({...obj,width: 200}))
    }

    return (
        <div style={{ height: 400, width: '100%' }}>
            <DataGrid
                getRowId={() => uuidv4()}
                rows={data.records}
                columns={modifyColumn(data.columns)}
                initialState={{
                pagination: {
                    paginationModel: { page: 0, pageSize: 5 },
                },
                }}
                pageSizeOptions={[5, 10]}
                sx={{'&.MuiDataGrid-root': {
                    border: 'none',
                }}}
            />
        </div>
    );
}