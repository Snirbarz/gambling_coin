(function () {
  const jsPsych = initJsPsych({
    display_element: document.querySelector('#jspsych-target'),
  });

  const timeline = [];

  const imageIds = [
    '01',
    '02',
    '03',
    '04',
    '05',
    '06',
    '07',
    '08',
    '09',
    '10',
  ];

  const preload = {
    type: jsPsychPreload,
    auto_preload: true,
    images: imageIds.map((id) => `data/Circ${id}.png`),
  };
  timeline.push(preload);

  const participantInfo = {};

  timeline.push({
    type: jsPsychSurveyHtmlForm,
    preamble:
      '<div class="instructions">מלא/י את פרטי ההשתתפות לפני תחילת המשימה.</div>',
    html: `
      <label>תאריך הניסוי</label>
      <input name="exp_date" type="date" required />
      <label>מספר נבדק/ת</label>
      <input name="participant_id" type="text" required />
    `,
    button_label: 'התחל/י',
    on_finish: (data) => {
      const responses = JSON.parse(data.responses);
      participantInfo.date = responses.exp_date;
      participantInfo.id = responses.participant_id.trim();
      jsPsych.data.addProperties({
        participant_id: participantInfo.id,
        session_date: participantInfo.date,
      });
    },
  });

  timeline.push({
    type: jsPsychHtmlButtonResponse,
    stimulus: `
      <div class="instructions">
        <p>ברוכים הבאים למשימת ההימורים. בתחילת המשימה תוצג לך מטבע אחת לשלב האימון, ולאחר מכן ארבע מטבעות נוספות בשני בלוקים.</p>
        <p>בכל ניסוי תתבקש/י לדמיין תוצאה או לצפות בתוצאה בפועל, ולאחר מכן להעריך ממוצעים, טווחים וביטחון.</p>
        <p>בהמשך תתבקש/י לבחור בין קבלת הפסד בטוח לבין הימור על תוצאת המטבע.</p>
        <p>לחץ/י על הכפתור כדי להתחיל.</p>
      </div>
    `,
    choices: ['התחל/י'],
    data: {
      event: 'instructions',
    },
  });

  function shuffle(array) {
    const result = array.slice();
    for (let i = result.length - 1; i > 0; i -= 1) {
      const j = Math.floor(Math.random() * (i + 1));
      [result[i], result[j]] = [result[j], result[i]];
    }
    return result;
  }

  function range(start, end) {
    const values = [];
    for (let v = start; v < end; v += 1) {
      values.push(v);
    }
    return values;
  }

  function chunk(array, size) {
    const chunks = [];
    for (let i = 0; i < array.length; i += size) {
      chunks.push(array.slice(i, i + size));
    }
    return chunks;
  }

  function lossSet(mu, spread) {
    return [
      mu + spread + 1,
      mu + spread + 1,
      mu + spread - 1,
      mu + spread - 1,
      mu + spread,
      mu + spread,
      mu - spread + 1,
      mu - spread + 1,
      mu - spread - 1,
      mu - spread - 1,
      mu - spread,
      mu - spread,
    ];
  }

  function outcomePattern(headSide) {
    if (headSide === 1) {
      return [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1];
    }
    return [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0];
  }

  function buildExperiment() {
    const noTrials = 5;
    const muValues = [-10, -10, -10, -10, -10];
    const sdLabels = ['MM', 'LH', 'HL', 'LH', 'HL'];

    const coinSidesBase = shuffle(range(0, 8));
    const coinSides = [8, 9, ...coinSidesBase];
    const coinSide1 = [
      coinSides[0],
      coinSides[2],
      coinSides[3],
      coinSides[4],
      coinSides[5],
    ];
    const coinSide2 = [
      coinSides[1],
      coinSides[6],
      coinSides[7],
      coinSides[8],
      coinSides[9],
    ];

    for (let i = 0; i < coinSide1.length; i += 1) {
      if (coinSide1[i] > coinSide2[i]) {
        const tmp = coinSide1[i];
        coinSide1[i] = coinSide2[i];
        coinSide2[i] = tmp;
      }
    }

    const coinHeads = shuffle([0, 0, 0, 1, 1]);

    const stimGenerate = [0, ...shuffle(range(1, noTrials))];

    const coins = [];
    for (let idx = 0; idx < noTrials; idx += 1) {
      const sdLabel = sdLabels[idx];
      let sdImg = 3;
      let sdView = 3;
      if (sdLabel === 'LH') {
        sdImg = 1;
        sdView = 6;
      } else if (sdLabel === 'HL') {
        sdImg = 6;
        sdView = 1;
      }
      coins.push({
        index: idx,
        mu: muValues[stimGenerate[idx]],
        sdLabel,
        sdImg,
        sdView,
        sideLeft: coinSide1[idx],
        sideRight: coinSide2[idx],
        headSide: coinHeads[idx],
      });
    }

    const blocks = [
      { name: 'training', coinIndices: [0], trialCount: 24 },
      { name: 'block_1', coinIndices: [1, 2], trialCount: 48 },
      { name: 'block_2', coinIndices: [3, 4], trialCount: 48 },
    ];

    blocks.forEach((block) => {
      block.coins = block.coinIndices.map((idx) => coins[idx]);
    });

    return { coins, blocks };
  }

  function renderCoinPair(coin, options = {}) {
    const {
      highlight = null,
      stage = 'learning',
    } = options;
    const leftClass = ['coin-card'];
    const rightClass = ['coin-card'];
    if (stage === 'rate') {
      leftClass.push('small');
      rightClass.push('small');
    }
    if (highlight === 0) {
      leftClass.push('highlight');
    } else if (highlight === 1) {
      rightClass.push('highlight');
    }
    const leftImage = imageIds[coin.sideLeft];
    const rightImage = imageIds[coin.sideRight];
    return `
      <div class="coin-pair">
        <div class="${leftClass.join(' ')}">
          <img src="data/Circ${leftImage}.png" alt="coin side left" />
        </div>
        <div class="${rightClass.join(' ')}">
          <img src="data/Circ${rightImage}.png" alt="coin side right" />
        </div>
      </div>
    `;
  }

  function buildLearningTimeline(block) {
    const viewChunksByCoin = [];
    const imgChunksByCoin = [];

    block.coins.forEach((coin) => {
      const viewLosses = lossSet(coin.mu, coin.sdView);
      const imgLosses = lossSet(coin.mu, coin.sdImg);
      const outcomes = outcomePattern(coin.headSide);

      const viewTrials = viewLosses.map((loss, idx) => ({
        type: 'view',
        loss,
        outcome: outcomes[idx],
        coin,
      }));
      const imgTrials = imgLosses.map((loss, idx) => ({
        type: 'img',
        loss,
        outcome: outcomes[idx],
        coin,
      }));

      viewChunksByCoin.push(chunk(shuffle(viewTrials), 3));
      imgChunksByCoin.push(chunk(shuffle(imgTrials), 3));
    });

    const chunkCount = Math.max(
      ...viewChunksByCoin.map((set) => set.length),
      ...imgChunksByCoin.map((set) => set.length),
    );

    const orderedTrials = [];
    for (let c = 0; c < chunkCount; c += 1) {
      block.coins.forEach((coin, idx) => {
        const viewChunk = viewChunksByCoin[idx][c] || [];
        const imgChunk = imgChunksByCoin[idx][c] || [];
        viewChunk.forEach((trial) => {
          orderedTrials.push({ ...trial, blockName: block.name });
        });
        imgChunk.forEach((trial) => {
          orderedTrials.push({ ...trial, blockName: block.name });
        });
      });
    }

    return orderedTrials;
  }

  function learningTrialEvents(trial, index) {
    const stageText =
      trial.type === 'img'
        ? 'בבקשה דמיין/י כאילו התוצאה המסומנת בירוק היא תוצאת ההטלה.\nלחץ/י על מקש הרווח להמשך.'
        : 'על מנת לצפות בתוצאה האמיתית של המטבע, לחץ/י על מקש הרווח.';

    const learningDisplay = {
      type: jsPsychHtmlKeyboardResponse,
      stimulus: () => {
        return `
          ${renderCoinPair(trial.coin, {
            highlight: trial.type === 'img' ? trial.outcome : null,
          })}
          <div class="status-text">${stageText}</div>
        `;
      },
      choices: [' '],
      data: {
        event: 'learning_display',
        block: trial.blockName,
        learning_mode: trial.type,
        loss_value: trial.loss,
        outcome_side: trial.outcome,
        coin_index: trial.coin.index,
        coin_side_left: trial.coin.sideLeft,
        coin_side_right: trial.coin.sideRight,
        mu: trial.coin.mu,
        sd_label: trial.coin.sdLabel,
        head_side: trial.coin.headSide,
        trial_index: index,
      },
    };

    const viewingPhase = {
      type: jsPsychHtmlKeyboardResponse,
      stimulus: () => {
        const caption =
          trial.type === 'img'
            ? 'דמיין/י את התוצאה המסומנת.'
            : 'הטלת המטבע מוצגת כעת.';
        return `
          ${renderCoinPair(trial.coin, {
            highlight: trial.outcome,
          })}
          <div class="status-text">${caption}</div>
        `;
      },
      choices: 'NO_KEYS',
      trial_duration: 1500,
      data: {
        event: 'learning_phase',
        block: trial.blockName,
        learning_mode: trial.type,
        loss_value: trial.loss,
        outcome_side: trial.outcome,
        coin_index: trial.coin.index,
        coin_side_left: trial.coin.sideLeft,
        coin_side_right: trial.coin.sideRight,
        mu: trial.coin.mu,
        sd_label: trial.coin.sdLabel,
        head_side: trial.coin.headSide,
        trial_index: index,
      },
    };

    const outcomeScreen = {
      type: jsPsychHtmlKeyboardResponse,
      stimulus: () => `
        <div class="outcome-display">${trial.loss}</div>
      `,
      choices: 'NO_KEYS',
      trial_duration: 1500,
      data: {
        event: 'learning_outcome',
        block: trial.blockName,
        learning_mode: trial.type,
        loss_value: trial.loss,
        outcome_side: trial.outcome,
        coin_index: trial.coin.index,
        coin_side_left: trial.coin.sideLeft,
        coin_side_right: trial.coin.sideRight,
        mu: trial.coin.mu,
        sd_label: trial.coin.sdLabel,
        head_side: trial.coin.headSide,
        trial_index: index,
      },
    };

    return [learningDisplay, viewingPhase, outcomeScreen];
  }

  function buildGamblingTimeline(block) {
    const timelineEvents = [];

    block.coins.forEach((coin) => {
      timelineEvents.push({
        type: jsPsychHtmlButtonResponse,
        stimulus: `
          <div class="instructions">
            <p>בחלק הבא תבחר/י האם להמר על תוצאת המטבע או לבחור בהפסד בטוח.</p>
            <p>להמר: מקש D. &nbsp;&nbsp; לקבל הפסד בטוח: מקש K.</p>
            <p>לחץ/י על הכפתור כדי להמשיך.</p>
          </div>
        `,
        choices: ['המשך'],
        data: {
          event: 'gamble_intro',
          block: block.name,
          coin_index: coin.index,
          coin_side_left: coin.sideLeft,
          coin_side_right: coin.sideRight,
          mu: coin.mu,
          sd_label: coin.sdLabel,
        },
      });

      const sureOptionsBase = [
        coin.mu + coin.sdView + 1,
        coin.mu + coin.sdView - 1,
        coin.mu + coin.sdView,
        coin.mu - coin.sdView - 1,
        coin.mu - coin.sdView + 1,
        coin.mu - coin.sdView,
        coin.mu + coin.sdImg + 1,
        coin.mu + coin.sdImg - 1,
        coin.mu + coin.sdImg,
        coin.mu - coin.sdImg - 1,
        coin.mu - coin.sdImg + 1,
        coin.mu - coin.sdImg,
      ];
      const sureOptions = sureOptionsBase.concat(sureOptionsBase);
      const lossArrayView = [
        coin.mu + coin.sdView + 1,
        coin.mu + coin.sdView - 1,
        coin.mu + coin.sdView,
        coin.mu - coin.sdView - 1,
        coin.mu - coin.sdView + 1,
        coin.mu - coin.sdView,
      ];
      const lossArrayAll = [
        coin.mu + coin.sdView + 1,
        coin.mu + coin.sdView - 1,
        coin.mu + coin.sdView,
        coin.mu - coin.sdView - 1,
        coin.mu - coin.sdView + 1,
        coin.mu - coin.sdView,
        coin.mu + coin.sdImg + 1,
        coin.mu + coin.sdImg - 1,
        coin.mu + coin.sdImg,
        coin.mu - coin.sdImg - 1,
        coin.mu - coin.sdImg + 1,
        coin.mu - coin.sdImg,
      ];

      const gambleBlocks = block.trialCount === 24 ? 2 : 4;

      for (let l = 0; l < gambleBlocks; l += 1) {
        const useImagery = l % 2 === 1;
        const instructionText = useImagery
          ? 'כעת ניתן להשתמש גם בתוצאות שהודמיינו בהחלטה שלך.'
          : 'כעת הסתמכי רק על התוצאות האמיתיות שראית.';
        timelineEvents.push({
          type: jsPsychHtmlButtonResponse,
          stimulus: `
            <div class="instructions">
              <p>${instructionText}</p>
              <p>לחץ/י על הכפתור כדי להמשיך.</p>
            </div>
          `,
          choices: ['המשך'],
          data: {
            event: 'gamble_instruction',
            block: block.name,
            coin_index: coin.index,
            use_imagery: useImagery ? 1 : 0,
          },
        });

        const shuffledOptions = shuffle(sureOptions);

        shuffledOptions.forEach((sureOption, optionIndex) => {
          timelineEvents.push({
            type: jsPsychHtmlKeyboardResponse,
            stimulus: '<div class="fixation">+</div>',
            choices: 'NO_KEYS',
            trial_duration: 500,
            data: {
              event: 'gamble_fixation',
              block: block.name,
              coin_index: coin.index,
              coin_side_left: coin.sideLeft,
              coin_side_right: coin.sideRight,
              mu: coin.mu,
              sd_label: coin.sdLabel,
              use_imagery: useImagery ? 1 : 0,
            },
          });

          timelineEvents.push({
            type: jsPsychHtmlKeyboardResponse,
            stimulus: () => `
              ${renderCoinPair(coin, { stage: 'gamble' })}
              <div class="status-text">הפסד בטוח: <strong>${sureOption}</strong> (מקש K)\nאו הימור על המטבע (מקש D)</div>
            `,
            choices: ['d', 'k'],
            data: {
              event: 'gamble_choice',
              block: block.name,
              coin_index: coin.index,
              coin_side_left: coin.sideLeft,
              coin_side_right: coin.sideRight,
              mu: coin.mu,
              sd_label: coin.sdLabel,
              sure_option: sureOption,
              use_imagery: useImagery ? 1 : 0,
              option_index: optionIndex,
            },
            on_finish: (data) => {
              const choiceKey = data.response;
              const gambled = choiceKey === 'd';
              const pool = gambled
                ? useImagery
                  ? lossArrayAll
                  : lossArrayView
                : [sureOption];
              const loss = shuffle(pool)[0];
              data.gambled = gambled ? 1 : 0;
              data.loss_value = loss;
            },
          });

          timelineEvents.push({
            type: jsPsychHtmlKeyboardResponse,
            stimulus: () => {
              const lastChoice = jsPsych.data.get().last(1).values()[0];
              return `
                <div class="outcome-display">${lastChoice.loss_value}</div>
              `;
            },
            choices: 'NO_KEYS',
            trial_duration: 1200,
            data: {
              event: 'gamble_outcome',
              block: block.name,
              coin_index: coin.index,
              coin_side_left: coin.sideLeft,
              coin_side_right: coin.sideRight,
              mu: coin.mu,
              sd_label: coin.sdLabel,
              use_imagery: useImagery ? 1 : 0,
            },
          });
        });
      }

      timelineEvents.push({
        type: jsPsychHtmlSliderResponse,
        stimulus: () => `
          ${renderCoinPair(coin, { stage: 'rate' })}
          <div class="status-text">בחר/י את ההפסד הממוצע של התוצאות האמיתיות בשלב הלמידה.</div>
        `,
        require_movement: true,
        labels: ['-20', '-10', '0'],
        min: -20,
        max: 0,
        step: 0.1,
        slider_start: -10,
        data: {
          event: 'estimate_mu',
          block: block.name,
          coin_index: coin.index,
          coin_side_left: coin.sideLeft,
          coin_side_right: coin.sideRight,
          mu: coin.mu,
          sd_label: coin.sdLabel,
        },
      });

      timelineEvents.push({
        type: jsPsychHtmlSliderResponse,
        stimulus: () => `
          ${renderCoinPair(coin, { stage: 'rate' })}
          <div class="status-text">כמה בטוח/ה את/ה בהערכה שלך (0 עד 100)?</div>
        `,
        require_movement: true,
        labels: ['0', '50', '100'],
        min: 0,
        max: 100,
        step: 5,
        slider_start: 50,
        data: {
          event: 'confidence_mu',
          block: block.name,
          coin_index: coin.index,
          coin_side_left: coin.sideLeft,
          coin_side_right: coin.sideRight,
          mu: coin.mu,
          sd_label: coin.sdLabel,
        },
      });

      timelineEvents.push({
        type: jsPsychSurveyHtmlForm,
        preamble: `
          <div class="instructions">
            <p>בחר/י את ההפסדים הנמוך והגבוה ביותר של התוצאות האמיתיות שראית.</p>
            <p>השתמש/י במכוונים כדי לבחור את הערכים ולאחר מכן לחץ/י המשך.</p>
          </div>
        `,
        html: `
          <div class="slider-wrapper">
            <label>ההפסד הנמוך ביותר</label>
            <input type="range" name="low" min="-20" max="0" step="0.1" value="-12" />
            <div class="value-preview" data-for="low">-12</div>
            <label>ההפסד הגבוה ביותר</label>
            <input type="range" name="high" min="-20" max="0" step="0.1" value="-8" />
            <div class="value-preview" data-for="high">-8</div>
          </div>
        `,
        button_label: 'המשך',
        on_load: () => {
          document.querySelectorAll('.slider-wrapper input[type="range"]').forEach((slider) => {
            slider.addEventListener('input', (event) => {
              const target = event.currentTarget;
              const valueBox = document.querySelector(
                `.value-preview[data-for="${target.name}"]`,
              );
              if (valueBox) {
                valueBox.textContent = target.value;
              }
            });
          });
        },
        data: {
          event: 'estimate_range',
          block: block.name,
          coin_index: coin.index,
          coin_side_left: coin.sideLeft,
          coin_side_right: coin.sideRight,
          mu: coin.mu,
          sd_label: coin.sdLabel,
        },
        on_finish: (data) => {
          const responses = JSON.parse(data.responses);
          data.range_low = parseFloat(responses.low);
          data.range_high = parseFloat(responses.high);
        },
      });

      timelineEvents.push({
        type: jsPsychHtmlSliderResponse,
        stimulus: () => `
          ${renderCoinPair(coin, { stage: 'rate' })}
          <div class="status-text">כמה בטוח/ה את/ה בהערכת הטווח (0 עד 100)?</div>
        `,
        require_movement: true,
        labels: ['0', '50', '100'],
        min: 0,
        max: 100,
        step: 5,
        slider_start: 50,
        data: {
          event: 'confidence_range',
          block: block.name,
          coin_index: coin.index,
          coin_side_left: coin.sideLeft,
          coin_side_right: coin.sideRight,
          mu: coin.mu,
          sd_label: coin.sdLabel,
        },
      });
    });

    return timelineEvents;
  }

  const experiment = buildExperiment();

  experiment.blocks.forEach((block) => {
    const learningTrials = buildLearningTimeline(block);
    learningTrials.forEach((trial, idx) => {
      timeline.push(...learningTrialEvents(trial, idx));
    });
    timeline.push(...buildGamblingTimeline(block));
  });

  timeline.push({
    type: jsPsychHtmlButtonResponse,
    stimulus: `
      <div class="instructions">
        <p>הניסוי הסתיים. תודה על ההשתתפות!</p>
        <p>לחץ/י על הכפתור כדי להוריד את הנתונים.</p>
      </div>
    `,
    choices: ['הורדת נתונים'],
    on_finish: () => {
      const filename = `gambling_${
        participantInfo.id || 'participant'
      }_${jsPsych.randomization.randomID(6)}.csv`;
      jsPsych.data.get().localSave('csv', filename);
    },
  });

  jsPsych.run(timeline);
})();
