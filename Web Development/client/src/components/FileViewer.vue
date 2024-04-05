<script setup>
import { ref, inject } from 'vue';
import axios from 'axios';
import { useLoading } from 'vue-loading-overlay'

const { uploadedFiles, removeFile, data_key, cleaning_time_info, rows_before_cleaning, duplicates_before_cleaning, nullvalues_before_cleaning, rows_after_cleaning, duplicates_after_cleaning, nullvalues_after_cleaning } = defineProps(['uploadedFiles', 'removeFile', 'data_key', 'cleaning_time_info', 'rows_before_cleaning', 'duplicates_before_cleaning', 'nullvalues_before_cleaning', 'rows_after_cleaning', 'duplicates_after_cleaning', 'nullvalues_after_cleaning']);
const indexToDelete = ref(null);
const filenameToDelete = ref(null);

const formatFileSize = (sizeInBytes) => {
    const units = ['B', 'KB', 'MB', 'GB', 'TB'];

    let size = sizeInBytes;
    let unitIndex = 0;

    while (size > 1024 && unitIndex < units.length - 1) {
        size /= 1024;
        unitIndex++;
    }

    return `${size.toFixed(2)} ${units[unitIndex]}`;
};

const setIndexAndFileNameToDelete = (index, filename) => {
    indexToDelete.value = index;
    filenameToDelete.value = filename;
};

const $loading = useLoading({
    // options
    color: '#000000',
    loader: 'dots',
    width: 128,
    height: 128,
    backgroundColor: '#ffffff',
    opacity: 0.5,
    "lock-scroll": true
});


const FLASK1_URL = 'http://127.0.0.1:3000'

const CleanData = async () => {
    console.log("uploading...");
    const headers = { 'Content-Type': 'multipart/form-data' };
    const loader = $loading.show({});

    try {
        const formData = new FormData();

        // Append each file to the FormData object
        uploadedFiles.forEach(file => {
            formData.append('file', file);
        });

        const response = await axios.post(`${FLASK1_URL}/cleandata`, formData, { headers });
        if (response.status == 200) {
            setTimeout(() => {
                loader.hide()
            }, 3000)
            setTimeout(() => {
                // Handle response from the server
                // const { data_key, cleaning_time_info, rows_before_cleaning, duplicates_before_cleaning, nullvalues_before_cleaning, rows_after_cleaning, duplicates_after_cleaning, nullvalues_after_cleaning } = response.data;
                // console.log(response.data);
                // console.log(data_key);
                // console.log(cleaning_time_info);
                // console.log(rows_before_cleaning);
                // console.log(duplicates_before_cleaning);
                // console.log(nullvalues_before_cleaning);
                // console.log(rows_after_cleaning);
                // console.log(duplicates_after_cleaning);
                // console.log(nullvalues_after_cleaning);

                // // Update the metrics on the webpage
                // document.getElementById('rows-before-cleaning').textContent = JSON.stringify(rows_before_cleaning);
                // document.getElementById('duplicates-before-cleaning').textContent = JSON.stringify(duplicates_before_cleaning);
                // document.getElementById('nullvalues-before-cleaning').textContent = JSON.stringify(nullvalues_before_cleaning);
                // document.getElementById('rows-after-cleaning').textContent = JSON.stringify(rows_after_cleaning);
                // document.getElementById('duplicates-after-cleaning').textContent = JSON.stringify(duplicates_after_cleaning);
                // document.getElementById('nullvalues-after-cleaning').textContent = JSON.stringify(nullvalues_after_cleaning);

                // Create a Blob from the binary data
                const blob = new Blob([response.data]);

                // Create a link element
                const url = window.URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;

                // Set the filename for the downloaded file
                link.setAttribute('download', 'cleaned_file.csv');

                // Append the link to the body and trigger the download
                document.body.appendChild(link);
                link.click();

                // Cleanup
                document.body.removeChild(link);
                window.URL.revokeObjectURL(url);

                aftercleaningmodal();
            }, 3000)
        }
    } catch (err) {
        throw new Error('Data Cleaning failed')
        // console.error('Data Analysis failed:', error);
    }
}

// Define rundescriptivediagnostic function
const aftercleaningmodal = async () => {

    // Display the modal once data analysis is done
    const modal = document.getElementById('cleaningModal');
    modal.style.display = "block";

    // Add event listener for the close button
    document.querySelector('.close-aftercleaning').addEventListener('click', async function () {
        // Hide the modal when the close button is clicked
        modal.style.display = "none";
        
    });
};


// Define DataAnalysis function separately
const DataAnalysis = async () => {
    console.log("Processing data analysis...")
    const headers = { 'Content-Type': 'multipart/form-data' };
    const loader = $loading.show({});

    try {
        const formData = new FormData();

        // Append each file to the FormData object
        uploadedFiles.forEach(file => {
            console.log(file);
            formData.append('file', file);
        });

        const sessionId = "001" // current storing a default value
        sessionStorage.setItem("sessionId", sessionId);
        formData.append('sessionId', sessionId);

        // console.log(formData)
        const response = await axios.post(`${FLASK1_URL}/dataanalysis`, formData, { headers });
        sessionStorage.setItem('id', response.data.data_key);

        if (response.status == 200) {
            loader.hide()
            await analysiswithdashboard();

        }
    } catch (err) {
        console.log(err)
        throw new Error('Data Analysis failed')
        // console.error('Data Analysis failed:', error);
    }
};

// Define navigatetosummarystatsclv function separately
const navigatetodashboard = async () => {
    window.location.href = '../dashboard.html';
};

// Define rundescriptivediagnostic function
const analysiswithdashboard = async () => {
    // Call the DataAnalysis function
    // await DataAnalysis();

    // Display the modal once data analysis is done
    const modal = document.getElementById('analysisModal');
    modal.style.display = "block";

    // Add event listener for the close button
    document.querySelector('.close-afteranalysis').addEventListener('click', async function () {
        // Hide the modal when the close button is clicked
        modal.style.display = "none";

        // Call the navigatetodashboard function after the loader is closed
        const loader = $loading.show({});
        await navigatetodashboard();
    });
};

</script>

<template>
    <div v-if="uploadedFiles.length > 0" class="container fileViewer-container">
        <div v-for="(item, index) in uploadedFiles" :key="index" class="file-item auto-height">

            <div class="row d-flex align-items-center">
                <div class="col-sm-10">
                    <span style="font-size: 20px; font-weight:600">{{ item.name }}</span><br>
                    <span style="color: rgb(180, 180, 179); font-weight:500;">{{ formatFileSize(item.size) }}</span><br>
                    <span>Ready to Upload</span>
                </div>
                <div class="col-sm">
                    <!-- Delete icon -->
                    <svg mlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-x-lg"
                        data-bs-toggle="modal" data-bs-target="#staticBackdrop" viewBox="0 0 16 16"
                        @click="setIndexAndFileNameToDelete(index, item.name)">
                        <path
                            d="M2.146 2.854a.5.5 0 1 1 .708-.708L8 7.293l5.146-5.147a.5.5 0 0 1 .708.708L8.707 8l5.147 5.146a.5.5 0 0 1-.708.708L8 8.707l-5.146 5.147a.5.5 0 0 1-.708-.708L7.293 8z" />
                    </svg>
                </div>
            </div>
        </div>

        <!-- Analysis Options -->
        <!-- Analyze multiple files -->
        <div class="row justify-content-left" v-if="uploadedFiles.length > 1">
            <div class="col-auto">

                <span style="margin-right: 10px;">Analysis Options:</span>
                <!-- Data Cleaning button -->
                <button type="button" class="btn btn-secondary"
                    style="margin-bottom: 10px; margin-top: 10px; margin-right: 10px;" data-bs-toggle="modal"
                    data-bs-target="#dcModal">
                    <span class="align-middle">Data Cleaning</span>
                </button>

                <!-- Descriptive & Diagnostic Analysis button -->
                <button type="button" class="btn btn-secondary" style="margin-bottom: 10px; margin-top: 10px;"
                    data-bs-toggle="modal" data-bs-target="#ddModal">
                    <span class="align-middle">Data Analysis</span>
                </button>
            </div>
        </div>

        <!-- Analyzing one file -->
        <div class="row justify-content-left" v-else>
            <div class="col-auto">

                <span style="margin-right: 10px;">Analysis Options:</span>
                <!-- Data Cleaning button -->
                <button type="button" class="btn btn-secondary"
                    style="margin-bottom: 10px; margin-top: 10px; margin-right: 10px;" data-bs-toggle="modal"
                    data-bs-target="#dcModal">
                    <span class="align-middle">Data Cleaning</span>
                </button>

                <!-- Descriptive & Diagnostic Analysis button -->
                <button type="button" class="btn btn-secondary" style="margin-bottom: 10px; margin-top: 10px;"
                    data-bs-toggle="modal" data-bs-target="#ddModal">
                    <span class="align-middle">Data Analysis</span>
                </button>

            </div>

            <div id="rows-before-cleaning">
                {{ rows_before_cleaning }}
            </div>
            <div id="duplicates-before-cleaning">
                {{ duplicates_before_cleaning }}
            </div>
            <div id="nullvalues-before-cleaning">
                {{ nullvalues_before_cleaning }}
            </div>
            <div id="rows-after-cleaning">
                {{ rows_after_cleaning }}
            </div>
            <div id="duplicates-after-cleaning">
                {{ duplicates_after_cleaning }}
            </div>
            <div id="nullvalues-after-cleaning">
                {{ nullvalues_after_cleaning }}
            </div>

        </div>

        <!-- Pop up to confirm deleting of the file -->
        <div class="modal fade" id="staticBackdrop" data-bs-backdrop="static" data-bs-keyboard="false" tabindex="-1"
            aria-labelledby="staticBackdropLabel" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header border-0">
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body border-0 text-center">
                        <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" fill="#dc3545"
                            class="bi bi-exclamation-triangle-fill" viewBox="0 0 16 16">
                            <path
                                d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5m.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2" />
                        </svg>
                        <br><br>
                        <h4>Delete this file? </h4>
                        <h6>{{ filenameToDelete }} will be deleted and this action cannot be undone.</h6>
                    </div>
                    <div class="modal-footer border-0">
                        <button type="button" class="btn btn-light border-light-subtle"
                            data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-danger" data-bs-dismiss="modal"
                            @click="removeFile(indexToDelete)">Delete</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Data Cleaning confirmation pop up -->
        <div class="modal fade" id="dcModal" data-bs-backdrop="static" data-bs-keyboard="false" tabindex="-1"
            aria-labelledby="staticBackdropLabel" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header border-0">
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body border-0 text-center">
                        <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" fill="#AAD9BB"
                            class="bi bi-check-circle-fill" viewBox="0 0 16 16">
                            <path
                                d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0m-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z" />
                        </svg>
                        <br><br>
                        <h4>Analysis Option: Data Cleaning Selected.</h4>
                        <h5>You can download the cleaned file once data cleaning is completed.</h5>
                    </div>
                    <div class="modal-footer border-0">
                        <button type="button" class="btn btn-light border-light-subtle" data-bs-dismiss="modal"
                            @click="CleanData()">Start Cleaning</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Descriptive & Diagnostic confirmation pop up -->
        <div class="modal fade" id="ddModal" data-bs-backdrop="static" data-bs-keyboard="false" tabindex="-1"
            aria-labelledby="staticBackdropLabel" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header border-0">
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body border-0 text-center">
                        <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" fill="#AAD9BB"
                            class="bi bi-check-circle-fill" viewBox="0 0 16 16">
                            <path
                                d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0m-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z" />
                        </svg>
                        <br><br>
                        <h4>Analysis Option: Data Analysis Selected </h4>
                    </div>
                    <div class="modal-footer border-0">
                        <button type="button" class="btn btn-light border-light-subtle" data-bs-dismiss="modal"
                            @click="DataAnalysis()">Start Analysis</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Cleaning Done Pop Up -->
        <div id="cleaningModal" class="modal-aftercleaning">
            <div class="modal-content-aftercleaning">
                <span class="close-aftercleaning">&times;</span>
                <h2>Data Cleaning Complete</h2>
                <p>Your data cleaning has finished successfully.</p>
                <p>Please check your downloads folder.</p>
                <p>Cleaning Time</p>
            </div>
        </div>

        <!-- Analysis Done Pop Up -->
        <div id="analysisModal" class="modal-afteranalysis">
            <div class="modal-content-afteranalysis">
                <span class="close-afteranalysis">&times;</span>
                <h2>Data Analysis Completed</h2>
                <p>Your data analysis has finished successfully.</p>
            </div>
        </div>



    </div>
</template>

<style scoped>
.auto-height {
    height: auto;
}

.fileViewer-container {
    width: 40%;
    border-right: 3px dashed rgb(180, 168, 168);
    border-bottom: 3px dashed rgb(180, 168, 168);
    border-left: 3px dashed rgb(180, 168, 168);
    overflow-x: auto;
    max-height: 400px;
}

.file-item {
    margin: 5px;
    border-bottom: 1px solid #ccc;
}

.modal-aftercleaning {
    display: none;
    position: fixed;
    z-index: 1;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    overflow: auto;
    background-color: rgba(0, 0, 0, 0.5);
}

.modal-content-aftercleaning {
    background-color: #fefefe;
    margin: 15% auto;
    padding: 20px;
    border: 1px solid #888;
    width: 80%;
    max-width: 600px;
}

.modal-afteranalysis {
    display: none;
    position: fixed;
    z-index: 1;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    overflow: auto;
    background-color: rgba(0, 0, 0, 0.5);
}

.modal-content-afteranalysis {
    background-color: #fefefe;
    margin: 15% auto;
    padding: 20px;
    border: 1px solid #888;
    width: 80%;
    max-width: 600px;
}

.close-aftercleaning {
    color: #aaa;
    float: right;
    font-size: 28px;
    font-weight: bold;
}

.close-aftercleaning:hover,
.close-aftercleaning:focus {
    color: black;
    text-decoration: none;
    cursor: pointer;
}

.close-afteranalysis {
    color: #aaa;
    float: right;
    font-size: 28px;
    font-weight: bold;
}

.close-afteranalysis:hover,
.close-afteranalysis:focus {
    color: black;
    text-decoration: none;
    cursor: pointer;
}
</style>