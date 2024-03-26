import { ref } from "vue";

export default function useDropZone() {
    const dragActive = ref(false);
    const droppedFile = ref(null);
    const uploadedFiles = ref([]);

    const toggle_active = () => {
        if (droppedFile.value == null) {
            dragActive.value = !dragActive.value;
        }
    };

    const isFileAlreadyUploaded = (file) => {
        return uploadedFiles.value.some(
            (uploadedFile) =>
                uploadedFile.name === file.name && uploadedFile.size === file.size
        );
    };

    const isValidFileType = (file) => {
        const allowedFileTypes = [".csv", ".xlsx", ".json"];
        const fileType = `.${file.name.split(".").pop()}`;
        return allowedFileTypes.includes(fileType.toLowerCase());
    };

    const drop = (event) => {
        if (event.dataTransfer.files.length > 0) {
            for (let i = 0; i < event.dataTransfer.files.length; i++) {
                let userFile = event.dataTransfer.files[i];
                
                if (!isValidFileType(userFile)) {
                    alert(`Invalid file type. Only .csv, .xlsx and .json files are allowed.`);
                    dragActive.value = false;
                    return;
                }

                if (!droppedFile.value) {
                    droppedFile.value = userFile;
                    dragActive.value = false;

                    setTimeout(() => {
                        droppedFile.value = null;
                    }, 0);
                }

                if (!isFileAlreadyUploaded(userFile)) {
                    uploadedFiles.value.push(userFile);
                } else {
                    alert(`${userFile.name} is already added!`);
                }
            }
        }
    };

    const selectedFile = async (event) => {
        if (event.target.files.length > 0) {
            for (let i = 0; i < event.target.files.length; i++) {
                let userFile = event.target.files[i];

                if (!droppedFile.value) {
                    droppedFile.value = userFile;

                    setTimeout(() => {
                        droppedFile.value = null;
                    }, 0);
                }

                if (!isFileAlreadyUploaded(userFile)) {
                    uploadedFiles.value.push(userFile);
                } else {
                    alert(`${userFile.name} is already added!.`);
                }
            }
        }
    };

    const removeFile = (index) => {
        uploadedFiles.value.splice(index, 1);
    };
    
    return {
        dragActive,
        droppedFile,
        uploadedFiles,
        toggle_active,
        drop,
        selectedFile,
        removeFile
    }
}