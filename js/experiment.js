/**
 * Gambling Task - jsPsych Implementation for JATOS
 * Based on provided PsychoPy script and subsequent corrections.
 */

// --- Global Variables and Parameters ---
let jsPsych; // Will be initialized within jatos.onLoad
let participantId = ''; // To be collected at the start
const experimentDate = new Date().toISOString().slice(0, 10); // YYYY-MM-DD format
let saveFileName = `participant_data.csv`; // Default, will be updated

const n_total_coins = 5; // 1 training + 4 test coins
const Mu = [-10, -10, -10, -10, -10]; // Mean loss for each base coin type
const SD_conditions = ["MM", "LH", "HL", "LH", "HL"]; // SD conditions [Imagination, View] for coins 0-4
// SD mapping: MM = [3,3], LH = [1,6], HL = [6,1]

// --- Media Paths (relative to where index.html is served) ---
const image_stim_names = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10"];
const image_base_path = 'js/media/img/'; // Assuming media folder is alongside index.html
const video_base_path = 'js/media/video/';
const image_paths = image_stim_names.map(name => `${image_base_path}Circ${name}.png`);
const instruction_images = [
    `${image_base_path}instructions_1.JPG`,
    `${image_base_path}instructions_2.JPG`,
    `${image_base_path}instructions_3.JPG`
];
// IMPORTANT: Ensure this dummy video exists in your media/video folder
const dummy_video_path = `${video_base_path}Coin000000.mp4`;

// Store all required media files for preloading
let all_image_files = [...image_paths, ...instruction_images];
let all_video_files = [dummy_video_path]; // Start with dummy, others added dynamically

// --- Experiment Configuration Storage ---
let coin_assignments = {}; // Will store side indices, heads side, order etc.
let blockSureOptions = {}; // Stores sure options generated for each coin index

// --- Helper Functions ---

// Fisher-Yates (Knuth) Shuffle
function shuffleArray(array) {
    let currentIndex = array.length, randomIndex;
    while (currentIndex !== 0) {
        randomIndex = Math.floor(Math.random() * currentIndex);
        currentIndex--;
        [array[currentIndex], array[randomIndex]] = [array[randomIndex], array[currentIndex]];
    }
    return array;
}

// Generate random integer between min (inclusive) and max (exclusive)
function getRandomInt(min, max) {
  min = Math.ceil(min);
  max = Math.floor(max);
  return Math.floor(Math.random() * (max - min) + min);
}

// Get current time as HHMMSS
function getCurrentTime() {
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    return `${hours}${minutes}${seconds}`;
}

// --- Experiment Setup ---
// Generates coin assignments based on PsychoPy logic
function setupExperimentParameters() {
    console.log("Setting up experiment parameters...");
    // Define coin sides based on PsychoPy logic
    let test_sides = shuffleArray([0, 1, 2, 3, 4, 5, 6, 7]);
    let final_sides = [8, 9, ...test_sides]; // Training sides 8,9 first

    // Assign specific sides to coin_side_1 and coin_side_2 arrays
    let side1_indices = [final_sides[0], final_sides[2], final_sides[3], final_sides[4], final_sides[5]];
    let side2_indices = [final_sides[1], final_sides[6], final_sides[7], final_sides[8], final_sides[9]];

    // Ensure side 1 index < side 2 index for consistency
    for (let i = 0; i < n_total_coins; i++) {
        if (side1_indices[i] > side2_indices[i]) {
            [side1_indices[i], side2_indices[i]] = [side2_indices[i], side1_indices[i]];
        }
    }

    // Determine which side is 'heads' (associated with higher loss for outcome=1 in PsychoPy code)
    let coin_heads_side = shuffleArray([0, 0, 0, 1, 1]); // 0=side1 is heads, 1=side2 is heads

    // Determine the presentation order of the coins (coin 0 first, then shuffled 1-4)
    let test_coin_order = shuffleArray([1, 2, 3, 4]);
    let coin_presentation_order = [0, ...test_coin_order];

    // Store the configuration
    coin_assignments = {
        side1_indices: side1_indices, // Image index for side 1 of each coin
        side2_indices: side2_indices, // Image index for side 2 of each coin
        heads_side: coin_heads_side,    // Which side (0 or 1) is designated 'heads'
        presentation_order: coin_presentation_order, // Order coins [0, ...] are presented
        mu: Mu,
        sd_conditions: SD_conditions
    };
    console.log("Coin Assignments:", coin_assignments);

    // Generate required video filenames based on assignments
    generateVideoPaths(); // This populates all_video_files
}

// Generates list of video files needed based on coin assignments
function generateVideoPaths() {
    const side1_idxs = coin_assignments.side1_indices;
    const side2_idxs = coin_assignments.side2_indices;

    for (let i = 0; i < n_total_coins; i++) {
        const s1_idx = side1_idxs[i];
        const s2_idx = side2_idxs[i];
        // Ensure indices are valid before accessing image_stim_names
        if (s1_idx === undefined || s2_idx === undefined || s1_idx < 0 || s1_idx >= image_stim_names.length || s2_idx < 0 || s2_idx >= image_stim_names.length) {
            console.error(`Invalid side indices for coin ${i}: side1=${s1_idx}, side2=${s2_idx}`);
            continue; // Skip this coin if indices are bad
        }
        const s1_name = image_stim_names[s1_idx];
        const s2_name = image_stim_names[s2_idx];

        // Video for outcome 1 (shows side 1 image)
        all_video_files.push(`${video_base_path}Coin${s1_name}${s2_name}${s1_name}.mp4`);
        // Video for outcome 2 (shows side 2 image)
        all_video_files.push(`${video_base_path}Coin${s1_name}${s2_name}${s2_name}.mp4`);
    }
    // Remove duplicates
    all_video_files = [...new Set(all_video_files)];
    console.log("Required video files for preload:", all_video_files);
}


// --- Function to Create Trial Parameters for a Block ---
function createBlockParameters(coin_indices, n_learning_trials_per_condition) {
    let learning_trials_all_coins = [];
    let sure_options_all_coins = {}; // Local to this function call

    for (const coin_index of coin_indices) {
        // Ensure coin_index is valid before proceeding
         if (coin_index === undefined || coin_index < 0 || coin_index >= n_total_coins) {
            console.error(`Invalid coin_index received in createBlockParameters: ${coin_index}`);
            continue; // Skip processing for this invalid index
        }

        const current_mu = coin_assignments.mu[coin_index];
        const current_sd_cond = coin_assignments.sd_conditions[coin_index];
        const head_side = coin_assignments.heads_side[coin_index]; // 0 or 1

        if (current_mu === undefined || current_sd_cond === undefined || head_side === undefined) {
             console.error(`Missing parameters for coin_index ${coin_index} in coin_assignments.`);
             continue;
        }

        let loss_sd_img, loss_sd_view;
        if (current_sd_cond === "LH") { loss_sd_img = 1; loss_sd_view = 6; }
        else if (current_sd_cond === "HL") { loss_sd_img = 6; loss_sd_view = 1; }
        else { loss_sd_img = 3; loss_sd_view = 3; } // MM

        // Generate potential losses (matches PsychoPy logic)
        const view_losses = [
            current_mu + loss_sd_view + 1, current_mu + loss_sd_view + 1, current_mu + loss_sd_view - 1, current_mu + loss_sd_view - 1, current_mu + loss_sd_view, current_mu + loss_sd_view,
            current_mu - loss_sd_view + 1, current_mu - loss_sd_view + 1, current_mu - loss_sd_view - 1, current_mu - loss_sd_view - 1, current_mu - loss_sd_view, current_mu - loss_sd_view
        ];
        const img_losses = [
            current_mu + loss_sd_img + 1, current_mu + loss_sd_img + 1, current_mu + loss_sd_img - 1, current_mu + loss_sd_img - 1, current_mu + loss_sd_img, current_mu + loss_sd_img,
            current_mu - loss_sd_img + 1, current_mu - loss_sd_img + 1, current_mu - loss_sd_img - 1, current_mu - loss_sd_img - 1, current_mu - loss_sd_img, current_mu - loss_sd_img
        ];

        // Generate outcomes based on PsychoPy logic (outcome=0 -> side1, outcome=1 -> side2)
        const view_outcomes = (head_side === 1) ? [0,0,0,0,0,0, 1,1,1,1,1,1] : [1,1,1,1,1,1, 0,0,0,0,0,0];
        const img_outcomes = (head_side === 1) ? [0,0,0,0,0,0, 1,1,1,1,1,1] : [1,1,1,1,1,1, 0,0,0,0,0,0];

        // Combine and label learning trials for this coin
        let coin_learning_trials = [];
        for (let i = 0; i < view_losses.length; i++) {
            coin_learning_trials.push({ coin_index: coin_index, task_type: 'view', loss: view_losses[i], outcome: view_outcomes[i] });
        }
        for (let i = 0; i < img_losses.length; i++) {
            coin_learning_trials.push({ coin_index: coin_index, task_type: 'img', loss: img_losses[i], outcome: img_outcomes[i] });
        }
        learning_trials_all_coins.push(...coin_learning_trials);

        // Generate sure options for gambling (matches PsychoPy)
        const loss_array_view_gamble = [ current_mu+loss_sd_view+1, current_mu+loss_sd_view-1, current_mu+loss_sd_view, current_mu-loss_sd_view-1, current_mu-loss_sd_view+1, current_mu-loss_sd_view ];
        const loss_array_img_gamble = [ current_mu+loss_sd_img+1, current_mu+loss_sd_img-1, current_mu+loss_sd_img, current_mu-loss_sd_img-1, current_mu-loss_sd_img+1, current_mu-loss_sd_img ];
        const loss_array_all_gamble = [...loss_array_view_gamble, ...loss_array_img_gamble];

        // Store sure options for this coin globally
        blockSureOptions[coin_index] = {
            options: [...loss_array_all_gamble, ...loss_array_all_gamble], // Doubled options
            loss_pool_view: loss_array_view_gamble, // For gamble outcome calc (use_imagery=0)
            loss_pool_all: loss_array_all_gamble   // For gamble outcome calc (use_imagery=1)
        };
    }

    // Shuffle trials based on PsychoPy's interleaving logic (blocks of 3)
    let shuffled_final_trials = [];
    if (coin_indices.length === 1) { // Training block (1 coin)
        const coin = coin_indices[0];
        let view_trials = learning_trials_all_coins.filter(p => p.coin_index === coin && p.task_type === 'view');
        let img_trials = learning_trials_all_coins.filter(p => p.coin_index === coin && p.task_type === 'img');
        shuffleArray(view_trials);
        shuffleArray(img_trials);
        for (let i = 0; i < n_learning_trials_per_condition; i += 3) {
            shuffled_final_trials.push(...view_trials.slice(i, i + 3));
            shuffled_final_trials.push(...img_trials.slice(i, i + 3));
        }
    } else if (coin_indices.length === 2) { // Test blocks (2 coins)
        const coin1 = coin_indices[0];
        const coin2 = coin_indices[1];
        let view1 = learning_trials_all_coins.filter(p => p.coin_index === coin1 && p.task_type === 'view');
        let img1 = learning_trials_all_coins.filter(p => p.coin_index === coin1 && p.task_type === 'img');
        let view2 = learning_trials_all_coins.filter(p => p.coin_index === coin2 && p.task_type === 'view');
        let img2 = learning_trials_all_coins.filter(p => p.coin_index === coin2 && p.task_type === 'img');
        shuffleArray(view1); shuffleArray(img1); shuffleArray(view2); shuffleArray(img2);
        for (let i = 0; i < n_learning_trials_per_condition; i += 3) {
            shuffled_final_trials.push(...view1.slice(i, i + 3));
            shuffled_final_trials.push(...img1.slice(i, i + 3));
            shuffled_final_trials.push(...view2.slice(i, i + 3));
            shuffled_final_trials.push(...img2.slice(i, i + 3));
        }
    }
     // Ensure the total number of trials matches expectation (e.g., 24 for training, 48 for test)
    const expected_total = coin_indices.length * n_learning_trials_per_condition * 2;
    shuffled_final_trials = shuffled_final_trials.slice(0, expected_total);

    console.log(`Generated ${shuffled_final_trials.length} learning trials for coins:`, coin_indices);

    return { learning_trials: shuffled_final_trials }; // Return only learning trials
}


// --- Define jsPsych Trial Objects ---

// Get Participant ID
const participant_id_trial = {
    type: jsPsychHtmlKeyboardResponse,
    stimulus: function() {
        // Use jatos.urlQueryParameters to potentially pre-fill ID if passed via URL
        const jatosId = jatos.urlQueryParameters.participantId || '';
        return `<p>Please enter participant ID:</p>
                <input type="text" id="participant-id" name="participant-id" value="${jatosId}" required><br><br>
                <button id="submit-id">Continue</button>`;
    },
    choices: "NO_KEYS", // Response handled by button click or Enter
    on_load: function() {
        const inputElement = document.getElementById('participant-id');
        const buttonElement = document.getElementById('submit-id');

        const submitId = () => {
             if (inputElement.value.trim() !== '') {
                participantId = inputElement.value.trim();
                // Remove listeners before finishing trial to prevent potential double triggers
                buttonElement.removeEventListener('click', submitId);
                inputElement.removeEventListener('keypress', handleKeypress);
                jsPsych.finishTrial({ participant_id: participantId });
            } else {
                alert('Participant ID cannot be empty.');
                inputElement.focus(); // Re-focus if empty
            }
        };

        const handleKeypress = (e) => {
            if (e.key === 'Enter') {
                 e.preventDefault(); // Prevent default Enter behavior (like form submission)
                 submitId();
            }
        };

        buttonElement.addEventListener('click', submitId);
        inputElement.addEventListener('keypress', handleKeypress);
        inputElement.focus(); // Focus the input field automatically
    },
    on_finish: function(data) {
        if (data.participant_id) {
            jsPsych.data.addProperties({ participant_id: data.participant_id }); // Add ID to all subsequent data
            saveFileName = `${experimentDate}_${data.participant_id}_gambling_task.csv`; // Update filename
            console.log(`Participant ID: ${data.participant_id}, Save filename: ${saveFileName}`);
            // Now setup parameters and generate video paths
            setupExperimentParameters(); // THIS IS CRITICAL - it defines coin_assignments
        } else {
            console.error("Participant ID was not captured correctly.");
            // Potentially end the study here if ID is crucial
            jatos.abortStudy("Error: Could not capture participant ID.");
        }
    }
};

// Preload Assets Trial
const preload_trial = {
    type: jsPsychPreload,
    // Use functions to ensure the arrays are populated *after* setupExperimentParameters runs
    images: () => all_image_files,
    video: () => all_video_files,
    show_progress_bar: true,
    continue_after_error: false, // Stop if media fails to load
    error_message: 'Error loading media files. Please check your internet connection and contact the experimenter if the problem persists.',
    message: 'Loading resources, please wait...'
};

// Welcome Screen
const welcome_screen = {
    type: jsPsychHtmlKeyboardResponse,
    stimulus: `<p style='font-size: 24px; direction: rtl;'>לחצ/י ENTER על מנת להתחיל</p>`, // Press ENTER to start
    choices: ['enter'],
    post_trial_gap: 250
};

// Instruction Screens
const instructions_learning_1 = {
    type: jsPsychImageKeyboardResponse,
    stimulus: instruction_images[0],
    prompt: `<p style='font-size: 20px; direction: rtl;'>לחצ/י ENTER להמשיך</p>`, // Press ENTER to continue
    choices: ['enter'],
    stimulus_width: 1000
};
const instructions_learning_2 = {
    type: jsPsychImageKeyboardResponse,
    stimulus: instruction_images[1],
    prompt: `<p style='font-size: 20px; direction: rtl;'>לחצ/י ENTER להמשיך</p>`,
    choices: ['enter'],
    stimulus_width: 1000
};
const instructions_gamble_training = { // Specific instruction before first gamble block
    type: jsPsychImageKeyboardResponse,
    stimulus: instruction_images[2],
    prompt: `<p style='font-size: 20px; direction: rtl;'>לחצ/י ENTER להמשיך</p>`,
    choices: ['enter'],
    stimulus_width: 1000
};

// Fixation Cross Trials
const short_fixation_trial = { // Fixed 200ms (after learning outcome)
    type: jsPsychHtmlKeyboardResponse,
    stimulus: '<div class="fixation"></div>',
    choices: "NO_KEYS",
    trial_duration: 200,
    data: { task_phase: 'fixation_short' },
    post_trial_gap: 0
};
const gambling_fixation_trial = { // Fixed 400ms (before gamble choice)
    type: jsPsychHtmlKeyboardResponse,
    stimulus: '<div class="fixation"></div>',
    choices: "NO_KEYS",
    trial_duration: 400,
    data: { task_phase: 'fixation_gamble' },
    post_trial_gap: 0
};

// Experimenter Check Screen
const experimenter_check_screen = {
     type: jsPsychHtmlKeyboardResponse,
     stimulus: `<p style='font-size: 24px; direction: rtl;'>אנא קרא/י לנסיינ/ית<br><br>(לחץ/י V להמשיך)</p>`, // Please call the experimenter (Press V to continue)
     choices: ['v'], // Use 'v' as per PsychoPy code comment
     data: { task_phase: 'experimenter_check' }
};


// --- Learning Trial Components ---

const learning_stimulus_display = {
    type: jsPsychHtmlKeyboardResponse,
    stimulus: function() {
        // ... (stimulus logic remains the same)
        const coin_idx = jsPsych.timelineVariable('coin_index');
        const task = jsPsych.timelineVariable('task_type');
        const outcome_side = jsPsych.timelineVariable('outcome');

        // Add defensive checks here too, in case timeline variables are missing
        if (coin_idx === undefined || task === undefined || outcome_side === undefined) {
             console.error("Missing timeline variables in learning_stimulus_display stimulus:",
                           { coin_idx, task, outcome_side });
             // Return a default or error message if needed, though data function is main issue
        }

        const side1_img_idx = coin_assignments.side1_indices[coin_idx];
        const side2_img_idx = coin_assignments.side2_indices[coin_idx];
        const img1_src = image_paths[side1_img_idx];
        const img2_src = image_paths[side2_img_idx];

        let instruction_text = '';
        let highlight_circle = '';

        if (task === 'img') {
            instruction_text = `<p style='direction: rtl;'>בבקשה דמיין/י כאילו התוצאה המסומנת בירוק היא התוצאה של ההטלה<br>לחץ/י SPACE להמשיך</p>`;
            highlight_circle = `<div class='outcome-circle ${outcome_side === 0 ? 'outcome-circle-left' : 'outcome-circle-right'}'></div>`;
        } else { // view trial
            instruction_text = `<p style='direction: rtl;'>על מנת לצפות בתוצאה האמיתית של המטבע, לחץ/י SPACE</p>`;
        }

        return `
            <div class='coin-container-learning'>
                ${highlight_circle}
                <img src='${img1_src}' alt='Coin Side 1'>
                <img src='${img2_src}' alt='Coin Side 2'>
            </div>
            ${instruction_text}
        `;
    },
    choices: [' '], // Spacebar
    data: function() {
        const coin_idx = jsPsych.timelineVariable('coin_index');
        const block_phase = jsPsych.timelineVariable('block_phase');
        const task_type = jsPsych.timelineVariable('task_type');

        // Defensive check for timeline variables within data function
         if (coin_idx === undefined || block_phase === undefined || task_type === undefined) {
            console.error("Missing timeline variables in learning_stimulus_display data:",
                           { coin_idx, block_phase, task_type });
            // Return minimal data or defaults to avoid breaking subsequent trials entirely
             return {
                 trial: `learning_ERROR_MISSING_TVARS`,
                 time: getCurrentTime(),
                 id: participantId,
                 Date: experimentDate,
                 task_phase: 'learning_stimulus_display',
                 error: 'Missing timeline variables'
                 // Ensure essential keys for the *next* trial are present, even if undefined/null
                 // coin_index: undefined, // Or null
                 // current_task: undefined, // Or null
                 // _outcome_correct_side: undefined // Or null
             }
         }

        // Check if coin_assignments are ready (should be, but good practice)
        const muValue = (coin_assignments.mu && coin_assignments.mu[coin_idx] !== undefined) ? coin_assignments.mu[coin_idx] : 'ERROR_MU';
        const sdValue = (coin_assignments.sd_conditions && coin_assignments.sd_conditions[coin_idx] !== undefined) ? coin_assignments.sd_conditions[coin_idx] : 'ERROR_SD';
        const headValue = (coin_assignments.heads_side && coin_assignments.heads_side[coin_idx] !== undefined) ? coin_assignments.heads_side[coin_idx] : 'ERROR_HEAD';
        const side1Value = (coin_assignments.side1_indices && coin_assignments.side1_indices[coin_idx] !== undefined) ? coin_assignments.side1_indices[coin_idx] : 'ERROR_S1';
        const side2Value = (coin_assignments.side2_indices && coin_assignments.side2_indices[coin_idx] !== undefined) ? coin_assignments.side2_indices[coin_idx] : 'ERROR_S2';


        return {
            // Data structure matching PsychoPy output as closely as possible
            trial: `learning_${block_phase}_coin${coin_idx}_${task_type}`,
            time: getCurrentTime(),
            id: participantId,
            Date: experimentDate,
            fix_time: 'NA',
            response: 6666, // PsychoPy code for space press
            side_1_stim: side1Value,
            side_2_stim: side2Value,
            latency: 'NA', // Updated on_finish
            Block: block_phase,
            Mu: muValue,
            SD: sdValue,
            head: headValue, // Which side (0 or 1) is designated heads
            outcome: 'NA',
            task: 'comb',
            gamble_trial: 'no',
            loss: 'NA', // Updated after outcome display
            est_mu: 'NA', est_low: 'NA', est_high: 'NA',
            conf_mu: 'NA', conf_range: 'NA',
            current_task: task_type, // 'view' or 'img' for this trial --> SAVED
            use_imagery: 'NA',
            sure_option: 'NA',
            // --- FIX: Explicitly save coin_index ---
            coin_index: coin_idx, // --> SAVED
            // Internal data passed to subsequent stages
            task_phase: 'learning_stimulus_display', // Internal identifier
             _outcome_correct_side: jsPsych.timelineVariable('outcome'), // --> SAVED
            _loss_associated: jsPsych.timelineVariable('loss')
        };
    },
     on_finish: function(data) {
        // Add latency only if response was recorded (which it should be for keyboard response)
         if (data.rt !== null) {
            data.latency = data.rt;
         }
        // Optional: Log the data *after* on_finish completes, to see final state
        // console.log("learning_stimulus_display final data:", data);
    },
    post_trial_gap: 200
};

// You should also keep the defensive checks within learning_video_display stimulus function
// as previously added, just in case.

const learning_video_display = {
    type: jsPsychVideoKeyboardResponse, // Correct plugin name
    stimulus: function() {
        const prev_trial_data = jsPsych.data.get().last(1).values()[0];

        // Check if previous trial data exists and has necessary properties
        if (!prev_trial_data || prev_trial_data.current_task === undefined || prev_trial_data.coin_index === undefined || prev_trial_data._outcome_correct_side === undefined) {
            console.error("Missing data from previous trial needed for video selection:", prev_trial_data);
            return [dummy_video_path]; // Fallback to dummy video
        }

        const task = prev_trial_data.current_task;
        const coin_idx = prev_trial_data.coin_index;
        const outcome_side = prev_trial_data._outcome_correct_side;

        if (task === 'view') {
             if (coin_idx === undefined || coin_idx < 0 || !coin_assignments.side1_indices || !coin_assignments.side2_indices) {
                 console.error("Invalid coin_idx or missing coin_assignments for video selection:", coin_idx, coin_assignments);
                 return [dummy_video_path];
             }
            const s1_idx = coin_assignments.side1_indices[coin_idx];
            const s2_idx = coin_assignments.side2_indices[coin_idx];
            if (s1_idx === undefined || s2_idx === undefined || !image_stim_names[s1_idx] || !image_stim_names[s2_idx]) {
                 console.error("Invalid side indices or names for video filename:", s1_idx, s2_idx);
                 return [dummy_video_path];
            }
            const s1_name = image_stim_names[s1_idx];
            const s2_name = image_stim_names[s2_idx];
            const outcome_img_name = (outcome_side === 0) ? s1_name : s2_name;
            const video_filename = `coin${s1_name}${s2_name}${outcome_img_name}.mp4`; // Ensure MP4
            const full_video_path = `${video_base_path}${video_filename}`;
            console.log("Attempting to load video:", full_video_path);
            return [full_video_path];
        } else { // Imagination trial
            console.log("Loading dummy video for imagination trial.");
            return [dummy_video_path];
        }
    },
    choices: "NO_KEYS",
    trial_ends_after_video: true,
    autoplay: true,
    controls: false,
    data: function() {
         const prev_trial_data = jsPsych.data.get().last(1).values()[0];
         return {
            task_phase: 'learning_video',
            coin_index: prev_trial_data ? prev_trial_data.coin_index : 'ERROR_NO_PREV_DATA'
         };
    },
    post_trial_gap: 0
};

const learning_video_display = {
    type: jsPsychVideoKeyboardResponse, // Correct plugin name
    stimulus: function() {
        // Retrieve necessary info from the *previous* trial's data
        const prev_trial_data = jsPsych.data.get().last(1).values()[0];

        // --- Debugging: Check what data is retrieved ---
        // console.log("Previous trial data for video:", prev_trial_data);
        // ---

        // Check if previous trial data exists and has necessary properties
        if (!prev_trial_data || prev_trial_data.current_task === undefined || prev_trial_data.coin_index === undefined || prev_trial_data._outcome_correct_side === undefined) {
            console.error("Missing data from previous trial needed for video selection:", prev_trial_data);
            // Return dummy video or handle error appropriately
            return [dummy_video_path];
        }

        const task = prev_trial_data.current_task; // 'view' or 'img'
        const coin_idx = prev_trial_data.coin_index;
        const outcome_side = prev_trial_data._outcome_correct_side; // 0 or 1

        // console.log("Video selection - Task:", task, "Coin:", coin_idx, "Outcome Side:", outcome_side); // More detailed log

        if (task === 'view') {
            // Check if coin_idx is valid before accessing assignments
             if (coin_idx === undefined || coin_idx < 0 || !coin_assignments.side1_indices || !coin_assignments.side2_indices) {
                 console.error("Invalid coin_idx or missing coin_assignments for video selection:", coin_idx, coin_assignments);
                 return [dummy_video_path]; // Fallback
             }

            const s1_idx = coin_assignments.side1_indices[coin_idx];
            const s2_idx = coin_assignments.side2_indices[coin_idx];

            // Check if indices and names are valid
            if (s1_idx === undefined || s2_idx === undefined || !image_stim_names[s1_idx] || !image_stim_names[s2_idx]) {
                 console.error("Invalid side indices or names for video filename:", s1_idx, s2_idx);
                 return [dummy_video_path]; // Fallback
            }

            const s1_name = image_stim_names[s1_idx];
            const s2_name = image_stim_names[s2_idx];
            const outcome_img_name = (outcome_side === 0) ? s1_name : s2_name;

            // *** USE .mp4 EXTENSION ***
            const video_filename = `coin${s1_name}${s2_name}${outcome_img_name}.mp4`;
            const full_video_path = `${video_base_path}${video_filename}`;

            // --- Debugging: Log the exact path being generated ---
            console.log("Attempting to load video:", full_video_path);
            // ---

            return [full_video_path];

        } else { // Imagination trial
             // console.log("Loading dummy video for imagination trial.");
            return [dummy_video_path]; // Play the blank coin video (ensure coin000000.mp4 exists)
        }
    },
    choices: "NO_KEYS",
    trial_ends_after_video: true,
    autoplay: true, // Browser policies might still block this initially
    controls: false, // Keep false for experiment, set true for debugging if needed
    // prompt: '<p>Loading video...</p>', // Optional: Show a loading message
    // check_fn: function() { ... } // More advanced: check if video loaded, but start simple
    data: function() {
         const prev_trial_data = jsPsych.data.get().last(1).values()[0];
         return {
            task_phase: 'learning_video',
            // Ensure coin_index exists on prev_trial_data, otherwise provide default
            coin_index: prev_trial_data ? prev_trial_data.coin_index : 'ERROR_NO_PREV_DATA'
         };
    },
    post_trial_gap: 0
};
const learning_outcome_display = {
    type: jsPsychHtmlKeyboardResponse,
    stimulus: function() {
        // Get the associated loss from the stimulus trial data (which is now 2 trials back)
        const stimulus_trial_data = jsPsych.data.get().last(2).values()[0];
        const loss_val = stimulus_trial_data ? stimulus_trial_data._loss_associated : 'Error';
        return `<p style='font-size: 48px;'>${loss_val}</p>`; // Display the determined loss
    },
    choices: "NO_KEYS",
    trial_duration: 1500, // core.wait(1.5)
    data: { task_phase: 'learning_outcome_display' }, // Minimal data for this phase
    on_finish: function(){
        // Find the corresponding stimulus display trial data and update its 'loss' field
        const stimulus_trial_data = jsPsych.data.get().filter({task_phase: 'learning_stimulus_display'}).last(1).values()[0];
        if (stimulus_trial_data && stimulus_trial_data._loss_associated !== undefined) {
             // Find the data row for the stimulus display trial and modify it directly
             const trial_index = stimulus_trial_data.trial_index; // jsPsych adds trial_index automatically
             jsPsych.data.get().filter({trial_index: trial_index}).values()[0].loss = stimulus_trial_data._loss_associated;
        } else {
             console.warn("Could not find preceding learning_stimulus_display trial data or loss value to update.");
        }
    },
    post_trial_gap: 0 // Followed immediately by short fixation
};


// --- Rating Trial Components ---

// Helper to create rating trial structure
function createRatingStimulusHTML(coin_index, text_prompt) {
    const side1_idx = coin_assignments.side1_indices[coin_index];
    const side2_idx = coin_assignments.side2_indices[coin_index];
    const img1_src = image_paths[side1_idx];
    const img2_src = image_paths[side2_idx];
    return `
        <div style='width: 100%; max-width: 1000px; margin-bottom: 180px;'>
             <div style='margin-bottom: 20px; direction: rtl; font-size: 22px;'>
                 ${text_prompt}
             </div>
             <div class='coin-container-rate' style='margin-bottom: 20px;'>
                 <img src='${img1_src}' alt='Coin Side 1'>
                 <img src='${img2_src}' alt='Coin Side 2'>
             </div>
        </div>`;
}

// Shared keydown handler for rating sliders (ends trial on SPACE if moved)
function ratingSliderKeydownHandler(event) {
     if (event.key === ' ') { // Use event.key for modern browsers
         event.preventDefault();
         const sliderElement = jsPsych.getDisplayElement().querySelector('input[type=range]');
         if (!sliderElement) return;
         const slider_value = sliderElement.value;
         const currentTrial = jsPsych.getCurrentTrial(); // Get properties of the current trial object

         // Check if movement is required and if it happened
         if (currentTrial.require_movement) {
            const start_val = currentTrial.slider_start;
            // Compare as numbers, slider value might be string
            if (parseFloat(slider_value) === parseFloat(start_val)) {
               return; // Don't end if not moved
            }
         }

         // Prepare data to finish trial using the key defined in trial's data property
         let trial_data_output = {};
         const data_key = currentTrial.data.rating_data_key;
         trial_data_output[data_key] = parseFloat(slider_value); // Ensure it's a number

         // Clean up listener *before* finishing trial
         document.removeEventListener('keydown', ratingSliderKeydownHandler);
         jsPsych.finishTrial(trial_data_output);
     }
 }

// Shared on_load for rating sliders (adds keydown listener)
function ratingSliderOnLoad() {
    document.addEventListener('keydown', ratingSliderKeydownHandler);
    const sliderElement = jsPsych.getDisplayElement().querySelector('input[type=range]');
    // Try to focus the slider for potential keyboard navigation (browser dependent)
    if (sliderElement) { try { sliderElement.focus(); } catch (e) {} }
}

// Shared on_finish for rating sliders (cleans up listener just in case)
function ratingSliderOnFinish() {
    document.removeEventListener('keydown', ratingSliderKeydownHandler);
}

// Rating Trial Definitions (using shared handlers)
const rate_mu_trial = {
    type: jsPsychHtmlSliderResponse,
    stimulus: function() {
        const coin_idx = jsPsych.timelineVariable('coin_index');
        const text = "בחר/י את ההפסד הממוצע של התוצאות האמיתיות (לא בדמיון) של המטבע בשלב הלמידה.<br>בסיום לחצו SPACE";
        return createRatingStimulusHTML(coin_idx, text);
    },
    labels: ['-20', '-18', '-16', '-14', '-12', '-10', '-8', '-6', '-4', '-2', '0'],
    min: -20, max: 0, step: 0.1, slider_start: -10,
    require_movement: true, slider_width: 1000,
    prompt: '<p style="color: lightgrey; margin-top: 20px;">(לחץ SPACE לאישור)</p>',
    response_ends_trial: false, // Crucial: let keydown handler end the trial
    css_classes: ['rating-mu'], // For specific slider handle color styling
    data: { task_phase: 'rating_mu', coin_index: () => jsPsych.timelineVariable('coin_index'), rating_data_key: 'rating_mu_value' },
    on_load: ratingSliderOnLoad,
    on_finish: ratingSliderOnFinish
};

const rate_confidence_mu_trial = {
    type: jsPsychHtmlSliderResponse,
    stimulus: function() {
        const coin_idx = jsPsych.timelineVariable('coin_index');
        const text = "כמה בטוח/ה את/ה בהערכת הממוצע שלך מ-0 עד 100<br>כשאת/ה מסיים/ת לחצ/י SPACE";
        return createRatingStimulusHTML(coin_idx, text);
    },
    labels: ['0 (כלל לא)', '50', '100 (מאוד)'],
    min: 0, max: 100, step: 1, slider_start: 50,
    require_movement: true, slider_width: 1000,
    prompt: '<p style="color: lightgrey; margin-top: 20px;">(לחץ SPACE לאישור)</p>',
    response_ends_trial: false,
    css_classes: ['rating-confidence'],
    data: { task_phase: 'rating_confidence_mu', coin_index: () => jsPsych.timelineVariable('coin_index'), rating_data_key: 'rating_conf_mu_value' },
    on_load: ratingSliderOnLoad,
    on_finish: ratingSliderOnFinish
};

const rate_range_high_trial = { // Corresponds to PsychoPy "low" estimation (most negative)
    type: jsPsychHtmlSliderResponse,
    stimulus: function() {
        const coin_idx = jsPsych.timelineVariable('coin_index');
        const text_main = "בחר/י את ההפסד הגבוה והנמוך ביותר של התוצאות האמיתיות (לא בדמיון).";
        const text_high = "<br><br><b>ההפסד הגבוה ביותר (הכי שלילי)</b>";
        const text_end = "<br>כשאת/ה מסיים/ת לחצ/י SPACE";
        return createRatingStimulusHTML(coin_idx, text_main + text_high + text_end);
    },
    labels: ['-20', '-18', '-16', '-14', '-12', '-10', '-8', '-6', '-4', '-2', '0'],
    min: -20, max: 0, step: 0.1, slider_start: -15,
    require_movement: true, slider_width: 1000,
    prompt: '<p style="color: lightgrey; margin-top: 20px;">(לחץ SPACE לאישור)</p>',
    response_ends_trial: false,
    css_classes: ['rating-range'],
    data: { task_phase: 'rating_range_high', coin_index: () => jsPsych.timelineVariable('coin_index'), rating_data_key: 'rating_range_high_value' }, // PsychoPy 'low'
    on_load: ratingSliderOnLoad,
    on_finish: ratingSliderOnFinish
};

const rate_range_low_trial = { // Corresponds to PsychoPy "high" estimation (least negative)
    type: jsPsychHtmlSliderResponse,
    stimulus: function() {
        const coin_idx = jsPsych.timelineVariable('coin_index');
        const text_main = "בחר/י את ההפסד הגבוה והנמוך ביותר של התוצאות האמיתיות (לא בדמיון).";
        const text_low = "<br><br><b>ההפסד הנמוך ביותר (הכי קרוב ל-0)</b>";
        const text_end = "<br>כשאת/ה מסיים/ת לחצ/י SPACE";
        return createRatingStimulusHTML(coin_idx, text_main + text_low + text_end);
    },
    labels: ['-20', '-18', '-16', '-14', '-12', '-10', '-8', '-6', '-4', '-2', '0'],
    min: -20, max: 0, step: 0.1, slider_start: -5,
    require_movement: true, slider_width: 1000,
    prompt: '<p style="color: lightgrey; margin-top: 20px;">(לחץ SPACE לאישור)</p>',
    response_ends_trial: false,
    css_classes: ['rating-range'],
    data: { task_phase: 'rating_range_low', coin_index: () => jsPsych.timelineVariable('coin_index'), rating_data_key: 'rating_range_low_value' }, // PsychoPy 'high'
    on_load: ratingSliderOnLoad,
    on_finish: ratingSliderOnFinish
};

const rate_confidence_range_trial = {
    type: jsPsychHtmlSliderResponse,
    stimulus: function() {
        const coin_idx = jsPsych.timelineVariable('coin_index');
        const text = "כמה בטוח/ה את/ה בהערכת הטווח שלך מ-0 עד 100<br>כשאת/ה מסיים/ת לחצ/י SPACE";
        return createRatingStimulusHTML(coin_idx, text);
    },
    labels: ['0 (כלל לא)', '50', '100 (מאוד)'],
    min: 0, max: 100, step: 1, slider_start: 50,
    require_movement: true, slider_width: 1000,
    prompt: '<p style="color: lightgrey; margin-top: 20px;">(לחץ SPACE לאישור)</p>',
    response_ends_trial: false,
    css_classes: ['rating-confidence'],
    data: { task_phase: 'rating_confidence_range', coin_index: () => jsPsych.timelineVariable('coin_index'), rating_data_key: 'rating_conf_range_value' },
    on_load: ratingSliderOnLoad,
    on_finish: function(data) { // Special on_finish for the LAST rating trial
        ratingSliderOnFinish(); // Basic cleanup

        // --- Create and write the summary rating row ---
        const coin_idx = data.coin_index;
        const block_phase = jsPsych.timelineVariable('block_phase'); // Get block phase from the timeline context

        // Retrieve values from the preceding rating trials *for this specific coin*
        const getRatingValue = (taskPhase, ratingKey) => {
            const trialData = jsPsych.data.get().filter({ task_phase: taskPhase, coin_index: coin_idx }).last(1).values()[0];
            return trialData && trialData[ratingKey] !== undefined ? trialData[ratingKey] : 'NA';
        };

        const rating_summary = {
            trial: `rating_summary_coin${coin_idx}_${block_phase}`, // More specific ID
            time: getCurrentTime(),
            id: participantId,
            Date: experimentDate,
            Block: block_phase,
            sub_phase: 'rating_summary', // Indicate this is a summary row
            task: 'comb', // Associated learning task type
            coin_index: coin_idx, // Add coin index for easier filtering later
            side_1_stim: coin_assignments.side1_indices[coin_idx],
            side_2_stim: coin_assignments.side2_indices[coin_idx],
            Mu: coin_assignments.mu[coin_idx],
            SD: coin_assignments.sd_conditions[coin_idx],
            head: coin_assignments.heads_side[coin_idx],
            est_mu: getRatingValue('rating_mu', 'rating_mu_value'),
            conf_mu: getRatingValue('rating_confidence_mu', 'rating_conf_mu_value'),
            // Assign jsPsych values to match PsychoPy column names (low=most neg, high=least neg)
            est_low: getRatingValue('rating_range_high', 'rating_range_high_value'), // PsychoPy low = high negativity slider
            est_high: getRatingValue('rating_range_low', 'rating_range_low_value'), // PsychoPy high = low negativity slider
            conf_range: data.rating_conf_range_value !== undefined ? data.rating_conf_range_value : 'NA', // Value from this trial
            // Fields not relevant to rating summary, fill with 'NA'
            fix_time: 'NA', response: 'NA', latency: 'NA', current_task: 'NA',
            outcome: 'NA', gamble_trial: 'no', loss: 'NA', use_imagery: 'NA', sure_option: 'NA'
        };
        jsPsych.data.write(rating_summary); // Add this summary row to the data
        console.log("Rating Summary Saved for Coin:", coin_idx);
    }
};


// --- Gambling Trial Components ---

const gamble_instruction_trial = {
    type: jsPsychHtmlKeyboardResponse,
    stimulus: function() {
        const use_imagery = jsPsych.timelineVariable('use_imagery_condition'); // 0 or 1
        let line1 = "עכשיו, יש לך את ההזדמנות להשתמש במה שלמדת על תוצאות המטבע";
        let line2 = (use_imagery === 0) ?
                    "אבל, התוצאות שהתקבלו בדמיון, אינן רלבנטיות להחלטה שלך" :
                    "התוצאות שהתקבלו בדמיון רלבנטיות במידה דומה לשאר התוצאות בהחלטה שלך";
        let line3 = "לחץ/י ENTER להמשיך";
        return `<p style='font-size: 24px; direction: rtl;'>${line1}<br><br>${line2}<br><br>${line3}</p>`;
    },
    choices: ['enter'],
    data: function() {
        return {
            task_phase: 'gamble_instruction',
            coin_index: jsPsych.timelineVariable('coin_index'), // Add context
            use_imagery_instructed: jsPsych.timelineVariable('use_imagery_condition')
        };
    },
    post_trial_gap: 250
};

const gamble_choice_trial = {
    type: jsPsychHtmlKeyboardResponse,
    stimulus: function() {
        const coin_idx = jsPsych.timelineVariable('coin_index');
        const sure_opt = jsPsych.timelineVariable('sure_option');
        const side1_img_idx = coin_assignments.side1_indices[coin_idx];
        const side2_img_idx = coin_assignments.side2_indices[coin_idx];
        const img1_src = image_paths[side1_img_idx];
        const img2_src = image_paths[side2_img_idx];

        return `
            <div style='width: 100%; max-width: 800px; text-align: center;'>
                <div style='margin-bottom: 30px; direction: rtl;'>
                    <p style='font-size: 24px;'>לחצ/י D אם את/ה רוצה להמר על תוצאות המטבע</p>
                    <p style='font-size: 24px;'>אחרת, לחצ/י K אם את/ה מעדיפ/ה לקבל את ההפסד הבטוח</p>
                </div>
                <div style='display: flex; justify-content: space-around; align-items: center;'>
                    <!-- Gamble Option (Left) -->
                    <div style='text-align: center;'>
                        <div class='coin-container-gamble'>
                             <img src='${img1_src}' alt='Coin Side 1'>
                             <img src='${img2_src}' alt='Coin Side 2'>
                        </div>
                         <p style='margin-top: 10px; font-size: 28px; direction: rtl;'>מטבע<br>(לחץ D)</p>
                    </div>
                    <!-- Sure Loss Option (Right) -->
                     <div style='text-align: center;'>
                         <p style='font-size: 28px; direction: rtl;'>הפסד בטוח</p>
                         <p style='font-size: 40px; margin-top: 10px;'>${sure_opt}</p>
                         <p style='margin-top: 10px; font-size: 28px; direction: rtl;'>(לחץ K)</p>
                     </div>
                </div>
            </div>`;
    },
    choices: ['d', 'k'], // d=gamble, k=sure loss
    data: function() {
        const coin_idx = jsPsych.timelineVariable('coin_index');
        const use_imagery_cond = jsPsych.timelineVariable('use_imagery_condition');
        const sure_opt_val = jsPsych.timelineVariable('sure_option');
        const block_phase = jsPsych.timelineVariable('block_phase');
        return {
            // Core data row matching PsychoPy structure
            trial: `gamble_${block_phase}_coin${coin_idx}_sure${sure_opt_val}_img${use_imagery_cond}`,
            time: getCurrentTime(),
            id: participantId,
            Date: experimentDate,
            fix_time: 400, // From preceding fixation trial
            response: 'NA', // Updated on_finish (0=sure, 1=gamble)
            side_1_stim: coin_assignments.side1_indices[coin_idx],
            side_2_stim: coin_assignments.side2_indices[coin_idx],
            latency: 'NA', // Updated on_finish
            Block: block_phase,
            Mu: coin_assignments.mu[coin_idx],
            SD: coin_assignments.sd_conditions[coin_idx],
            head: coin_assignments.heads_side[coin_idx],
            outcome: 'NA', // Not applicable for choice itself
            task: 'comb', // Associated learning task type
            gamble_trial: 'yes',
            loss: 'NA', // Calculated and updated on_finish
            est_mu: 'NA', est_low: 'NA', est_high: 'NA',
            conf_mu: 'NA', conf_range: 'NA',
            current_task: 'NA', // Not a learning trial
            use_imagery: use_imagery_cond, // 0 or 1 for this specific trial
            sure_option: sure_opt_val,
             // Internal identifier
             task_phase: 'gamble_choice_trial'
        };
    },
    on_finish: function(data) {
        data.latency = data.rt;
        data.response = (data.response === 'd') ? 1 : 0; // 1=gamble, 0=sure

        // Calculate outcome loss based on choice and imagery condition
        const coin_idx = data.coin_index; // Retrieve from data object
        const sure_option = data.sure_option;
        const gamble_choice = data.response; // 0 or 1
        const use_imagery = data.use_imagery; // 0 or 1

        const coin_sure_options_pools = blockSureOptions[coin_idx];

        if (!coin_sure_options_pools) {
            console.error(`Sure option pools not found for coin index: ${coin_idx} in gamble trial on_finish.`);
            data.loss = 'ERROR_POOL_MISSING';
            return;
        }

        let loss_outcome;
        if (gamble_choice === 1) { // Participant chose to gamble
            let relevant_loss_pool = (use_imagery === 0) ?
                                     coin_sure_options_pools.loss_pool_view :
                                     coin_sure_options_pools.loss_pool_all;

            if (!relevant_loss_pool || relevant_loss_pool.length === 0) {
                 console.error(`Relevant loss pool is empty or undefined for coin ${coin_idx}, imagery=${use_imagery}`);
                 data.loss = 'ERROR_POOL_EMPTY';
                 return;
            }
            // Choose a random outcome from the relevant loss distribution
            loss_outcome = relevant_loss_pool[Math.floor(Math.random() * relevant_loss_pool.length)];
        } else { // Participant chose sure loss
            loss_outcome = sure_option;
        }
        data.loss = loss_outcome; // Update the loss field for this trial's data row
    }
};


// --- Timeline Creation Function ---
// Creates the full sequence for a block (learning + rating + gambling)
function createFullBlockTimeline(coin_indices, n_learning_trials_per_condition, block_phase_name, n_gamble_trials_per_instruction) {
    const block_timeline = [];

    // Generate learning trials (sure options were generated globally in setupExperimentParameters)
    const { learning_trials } = createBlockParameters(coin_indices, n_learning_trials_per_condition);

    // A. Learning Phase Procedure
    const learning_procedure = {
        timeline: [
            learning_stimulus_display,
            learning_video_display,
            learning_outcome_display,
            short_fixation_trial // Fixation after outcome
        ],
        timeline_variables: learning_trials.map(trial => ({ ...trial, block_phase: block_phase_name })), // Add block phase name
        data: { sub_phase: 'learning' } // General data for all learning trials in this block
    };
    block_timeline.push(learning_procedure);

    // B. Rating and Gambling Phase (Loop per coin in the block)
    for (const coin_index of coin_indices) {
        // Add Rating Procedure for this coin
        const rating_procedure = {
            timeline: [
                rate_mu_trial,
                rate_confidence_mu_trial,
                rate_range_high_trial, // PsychoPy low
                rate_range_low_trial,  // PsychoPy high
                rate_confidence_range_trial // This trial writes the summary row
            ],
            timeline_variables: [{ coin_index: coin_index, block_phase: block_phase_name }], // Pass context
            data: { coin_index: coin_index, sub_phase: 'rating' }
        };
        block_timeline.push(rating_procedure);

        // Add specific instructions/checks AFTER ratings, BEFORE gambling for training block coin 0
        if (block_phase_name === 'training' && coin_index === 0) {
             block_timeline.push(experimenter_check_screen);
             block_timeline.push(instructions_gamble_training); // Show specific gamble instruction image
        }

        // Add Gambling Procedure for this coin
        const n_gamble_instruction_blocks = (block_phase_name === 'training') ? 4 : 2;

        for (let gamble_instr_idx = 0; gamble_instr_idx < n_gamble_instruction_blocks; gamble_instr_idx++) {
            const use_imagery_condition = gamble_instr_idx % 2; // 0 = no imagery, 1 = use imagery

            // Add gambling instruction trial
            block_timeline.push({
                 ...gamble_instruction_trial,
                 timeline_variables: [{ use_imagery_condition: use_imagery_condition, coin_index: coin_index }], // Pass context
                 data: { block_phase: block_phase_name } // Add context
            });

            // Prepare and shuffle sure options for this specific gambling sub-block
            let current_sure_options_set = [];
            if (blockSureOptions[coin_index] && blockSureOptions[coin_index].options) {
                 current_sure_options_set = shuffleArray([...blockSureOptions[coin_index].options]); // Shuffle a copy
            } else {
                 console.error(`Sure options not found for coin ${coin_index} when creating gambling timeline.`);
                 continue; // Skip this gambling block if options missing
            }

            const start_idx = gamble_instr_idx * n_gamble_trials_per_instruction;
            const end_idx = start_idx + n_gamble_trials_per_instruction;
            const sub_block_sure_options = current_sure_options_set.slice(start_idx, end_idx);

            if(sub_block_sure_options.length < n_gamble_trials_per_instruction){
                console.warn(`Warning: Not enough sure options for coin ${coin_index}, block ${gamble_instr_idx}. Requested ${n_gamble_trials_per_instruction}, got ${sub_block_sure_options.length}`);
                 // Decide whether to continue with fewer trials or stop
                 if (sub_block_sure_options.length === 0) continue; // Skip if none available
            }

            const gamble_sub_block_procedure = {
                timeline: [
                    gambling_fixation_trial,
                    gamble_choice_trial
                ],
                timeline_variables: sub_block_sure_options.map(option => ({
                    coin_index: coin_index,
                    sure_option: option,
                    use_imagery_condition: use_imagery_condition, // Pass imagery condition
                    block_phase: block_phase_name // Pass block phase
                })),
                data: { sub_phase: 'gambling', use_imagery_block: use_imagery_condition }
            };
            block_timeline.push(gamble_sub_block_procedure);
        }
         // Optional: Marker trial for end of coin processing
         block_timeline.push({
            type: jsPsychHtmlKeyboardResponse, stimulus: '', trial_duration: 0, choices: 'NO_KEYS',
            data: { task_phase: 'end_of_coin_processing', coin_index: coin_index }
         });
    } // End loop over coins

    return block_timeline;
}

// --- End of Experiment Screen ---
const end_screen = {
    type: jsPsychHtmlKeyboardResponse,
    stimulus: function() {
        return `<p style='font-size: 24px;'>The experiment is complete.</p>
                <p>Submitting data...</p>
                <p>Please wait for confirmation before closing the window.</p>`;
    },
    choices: "NO_KEYS",
    trial_duration: null, // Wait indefinitely until JATOS confirms submission
    on_load: function() { // Use on_load to trigger submission immediately
        // Filter data to include only relevant trials (stimulus display, gamble choice, rating summary)
        const relevant_data = jsPsych.data.get().filter(trial =>
            trial.task_phase === 'learning_stimulus_display' ||
            trial.task_phase === 'gamble_choice_trial' ||
            trial.sub_phase === 'rating_summary'
        );

        // Select and order columns matching PsychoPy output structure
        const columns_to_keep = [
            'trial', 'time', 'id', 'Date', 'fix_time', 'response', 'side_1_stim',
            'side_2_stim', 'latency', 'Block', 'Mu', 'SD', 'head', 'outcome',
            'task', 'gamble_trial', 'loss', 'est_mu', 'est_low', 'est_high',
            'conf_mu', 'conf_range', 'current_task', 'use_imagery', 'sure_option',
            // Add internal identifiers if needed for debugging/analysis
            'coin_index', 'task_phase', 'sub_phase'
        ];
        const final_data_json = relevant_data.json(); // Get as JSON string for JATOS

        console.log(`Submitting ${relevant_data.count()} rows of data to JATOS.`);

        // Submit data to JATOS
        jatos.submitResultData(final_data_json)
            .then(() => {
                console.log("Data submission successful.");
                // Optionally, save CSV locally as a backup (might be blocked by browser)
                try {
                    relevant_data.localSave('csv', saveFileName, columns_to_keep);
                } catch (e) {
                    console.warn("Local CSV save failed (might be blocked by browser):", e);
                }
                // End the study in JATOS
                jatos.endStudyAjax(true, "Study completed successfully.")
                    .then(() => {
                         jsPsych.getDisplayElement().innerHTML = `<p style='font-size: 24px;'>Data submitted successfully. Thank you!<br>You may now close this window.</p>`;
                    })
                    .catch(err => {
                         console.error("Error ending study via AJAX:", err);
                         jsPsych.getDisplayElement().innerHTML = `<p style='font-size: 20px; color: orange;'>Data submitted, but there was an issue finalizing the study with the server.<br>Please contact the experimenter.<br>You may close this window.</p>`;
                    });

            })
            .catch((error) => {
                console.error("Data submission failed:", error);
                 // Save locally as a fallback
                 try {
                    relevant_data.localSave('csv', 'FAILED_SUBMISSION_' + saveFileName, columns_to_keep);
                    jsPsych.getDisplayElement().innerHTML = `<p style='font-size: 20px; color: red;'>Error submitting data to the server.<br>Your data has been saved locally as ${'FAILED_SUBMISSION_' + saveFileName}.<br>Please contact the experimenter and provide them with this file.<br>You may now close the window.</p>`;
                 } catch (e) {
                    console.error("Local backup save also failed:", e);
                    jsPsych.getDisplayElement().innerHTML = `<p style='font-size: 20px; color: red;'>CRITICAL ERROR: Data submission failed AND local backup save failed.<br>Please leave this window open and contact the experimenter immediately.</p>`;
                 }
                 // Optionally attempt to end study with failure status
                 jatos.abortStudy("Data submission failed.");
            });
    }
};


// --- Run Experiment Logic (within jatos.onLoad) ---
jatos.onLoad(() => {
    // Initialize jsPsych *inside* jatos.onLoad
    jsPsych = initJsPsych({
      on_trial_start: jatos.addAbortButton, // Add abort button to each trial
      // on_finish handled by the end_screen trial logic with jatos.endStudyAjax/abortStudy
    });

    // --- Define Setup Timeline ---
    const timeline_setup = [];
    timeline_setup.push(participant_id_trial); // Gets ID, calls setupExperimentParameters
    timeline_setup.push(preload_trial);       // Preloads media using generated paths

    // --- Run Setup Phase ---
    jsPsych.run(timeline_setup).then(() => {
        // --- Setup Complete - Build and Run Main Experiment ---
        console.log("Setup timeline complete. Participant ID:", participantId);

        // Critical check: Ensure coin_assignments were set up
        if (!coin_assignments || !coin_assignments.presentation_order || coin_assignments.presentation_order.length === 0) {
            console.error("CRITICAL ERROR: Experiment parameters (coin_assignments) were not set up after participant ID trial.");
            jatos.abortStudy("Critical error: Experiment parameters failed to initialize.");
            // Display error to participant
             try {
                jsPsych.getDisplayElement().innerHTML = `<p style='font-size: 20px; color: red;'>A critical error occurred during experiment setup.<br>The study cannot continue.<br>Please contact the experimenter.</p>`;
             } catch(e) {/* Display element might not be available */}
            return; // Stop execution
        }
        console.log("Coin assignments ready:", coin_assignments);

        // --- Build the MAIN experiment timeline ---
        const main_timeline = [];

        // Welcome & Initial Learning Instructions
        main_timeline.push(welcome_screen);
        main_timeline.push(instructions_learning_1);
        main_timeline.push(instructions_learning_2);

        // Block 1: Training
        const training_coin_indices = [coin_assignments.presentation_order[0]];
        const n_learn_train = 12; // 12 view + 12 img = 24 total learning
        const n_gamble_train = 6; // 24 sure options / 4 gamble blocks = 6 per block
        const training_timeline_nodes = createFullBlockTimeline(training_coin_indices, n_learn_train, 'training', n_gamble_train);
        main_timeline.push(...training_timeline_nodes);
        // Note: experimenter_check and gamble instructions are added *within* createFullBlockTimeline for coin 0

        // Block 2: Test Block 1
        const test_block1_coin_indices = coin_assignments.presentation_order.slice(1, 3);
        const n_learn_test = 12; // 12 view + 12 img per coin = 48 total learning
        const n_gamble_test = 12; // 24 sure options / 2 gamble blocks = 12 per block
        const test_block1_timeline_nodes = createFullBlockTimeline(test_block1_coin_indices, n_learn_test, 'test_block_1', n_gamble_test);
        main_timeline.push(experimenter_check_screen); // Check screen BETWEEN major blocks
        main_timeline.push(...test_block1_timeline_nodes);

        // Block 3: Test Block 2
        const test_block2_coin_indices = coin_assignments.presentation_order.slice(3, 5);
        const test_block2_timeline_nodes = createFullBlockTimeline(test_block2_coin_indices, n_learn_test, 'test_block_2', n_gamble_test);
        main_timeline.push(experimenter_check_screen); // Check screen BETWEEN major blocks
        main_timeline.push(...test_block2_timeline_nodes);

        // End Screen (handles data submission)
        main_timeline.push(end_screen);

        // --- Run the MAIN experiment ---
        console.log("Starting main experiment timeline...");
        jsPsych.run(main_timeline);

    }).catch(error => {
        // Handle errors during the setup phase (ID entry, preload)
        console.error("Error during setup timeline:", error);
        // Try to inform JATOS and the participant
        jatos.abortStudy(`Error during experiment setup: ${error.message || error}`);
         try {
                jsPsych.getDisplayElement().innerHTML = `<p style='font-size: 20px; color: red;'>A critical error occurred during experiment setup: ${error.message || error}<br>The study cannot continue.<br>Please contact the experimenter.</p>`;
         } catch(e) {/* Display element might not be available */}
    });

}); // End jatos.onLoad

