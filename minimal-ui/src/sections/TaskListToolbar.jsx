import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  IconButton,
  InputAdornment,
  OutlinedInput,
  TextField,
  Toolbar,
  Tooltip,
  Typography
} from "@mui/material";
import { alpha, styled } from "@mui/material/styles";
import PropTypes from "prop-types";
import { useState } from "react";
import { useNavigate } from 'react-router-dom';
import { backendApi } from "../api/api";
import { pipelineStore } from "../appState/pipelineStore";
import Iconify from "../components/Iconify";


const StyledRoot = styled(Toolbar)(({ theme }) => ({
  height: 96,
  display: "flex",
  justifyContent: "space-between",
  padding: theme.spacing(0, 1, 0, 3),
}));

const StyledSearch = styled(OutlinedInput)(({ theme }) => ({
  width: 240,
  transition: theme.transitions.create(["box-shadow", "width"], {
    easing: theme.transitions.easing.easeInOut,
    duration: theme.transitions.duration.shorter,
  }),
  "&.Mui-focused": {
    width: 320,
    boxShadow: theme.customShadows.z8,
  },
  "& fieldset": {
    borderWidth: `1px !important`,
    borderColor: `${alpha(theme.palette.grey[500], 0.32)} !important`,
  },
}));

TaskListToolbar.propTypes = {
  numSelected: PropTypes.number,
  filterName: PropTypes.string,
  onFilterName: PropTypes.func,
};

export default function TaskListToolbar({
  numSelected,
  filterName,
  onFilterName,
}) {

  const [pipelineName, setPipelineName] = useState('');
  const [, { setPipeline }] = pipelineStore()

  const handleChange = (event) => {
    setPipelineName(event.target.value);
  };

  const [open, setOpen] = useState(false);

  const handleClickOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  const navigate = useNavigate()

  async function createPipeline() {
    const response = await backendApi.post("/pipeline", {
      "name": pipelineName,
      "executor_config": {}
    })

    if (response.data.pipeline) {
      setPipeline(response.data.pipeline)
      navigate(`app/${response.data.pipeline.uuid}`, { replace: true })
    }

  }


  return (
    <>
      <StyledRoot
        sx={{
          ...(numSelected > 0 && {
            color: "primary.main",
            bgcolor: "primary.lighter",
          }),
        }}
      >
        {numSelected > 0 ? (
          <Typography component="div" variant="subtitle1">
            {numSelected} selected
          </Typography>
        ) : (
          <StyledSearch
            value={filterName}
            onChange={onFilterName}
            placeholder="Search pipeline..."
            startAdornment={
              <InputAdornment position="start">
                <Iconify
                  icon="eva:search-fill"
                  sx={{ color: "text.disabled", width: 20, height: 20 }}
                />
              </InputAdornment>
            }
          />
        )}

        {numSelected > 0 ? (
          <Tooltip title="Delete">
            <IconButton>
              <Iconify icon="eva:trash-2-fill" />
            </IconButton>
          </Tooltip>
        ) : (
          <Button variant="contained" onClick={handleClickOpen} startIcon={<Iconify icon="eva:plus-fill" />}>
            Create New Pipeline
          </Button>
        )}
      </StyledRoot>
      <div>
        <Dialog open={open} onClose={handleClose}>
          <DialogContent>
            <TextField margin="dense" id="pipeline-name" onChange={handleChange} label="Pipeline Name" type="text" fullWidth variant="standard" />
          </DialogContent>
          <DialogActions>
            <Button onClick={handleClose}>Cancel</Button>
            <Button onClick={createPipeline}>
              Create
            </Button>
          </DialogActions>
        </Dialog>
      </div>
    </>
  );
}
