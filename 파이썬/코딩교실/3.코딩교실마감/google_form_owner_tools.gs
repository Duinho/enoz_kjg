const CONFIG = Object.freeze({
  formId: '1MNdXWzIYEdQsWS607aL3voTfQCiRdzjXdaYutQmNzA8',
  roleQuestionKeyword: '참여 유형',
  parentSectionKeyword: '학부모',
  studentSectionKeyword: '학생',
  allowedRoles: ['학부모', '학생'],
  scoreWeights: [
    { score: 5, weight: 80 },
    { score: 4, weight: 15 },
    { score: 3, weight: 5 },
  ],
});

function submitParentsUntil180() {
  return submitRoleUntilTotal({
    targetTotal: 180,
    role: CONFIG.allowedRoles[0],
  });
}

function submitParentsUntil80() {
  return submitRoleUntilCount({
    targetCount: 80,
    role: CONFIG.allowedRoles[0],
  });
}

function submitRoleUntilTotal(options) {
  const settings = options || {};
  const targetTotal = Number(settings.targetTotal);
  const role = normalizeRole_(settings.role);

  if (!Number.isFinite(targetTotal) || targetTotal < 0) {
    throw new Error('targetTotal must be a non-negative number.');
  }
  if (!CONFIG.allowedRoles.includes(role)) {
    throw new Error(`role must be one of: ${CONFIG.allowedRoles.join(', ')}`);
  }

  const form = FormApp.openById(CONFIG.formId);
  const model = buildFormModel_(form);
  const summaryBefore = getFormSummary_();
  const delta = targetTotal - summaryBefore.validTotal;

  if (delta < 0) {
    throw new Error(`Current valid total ${summaryBefore.validTotal} already exceeds target ${targetTotal}.`);
  }
  if (delta === 0) {
    Logger.log('Nothing to add. Target already satisfied.');
    return summaryBefore;
  }

  const scaleItems = role === CONFIG.allowedRoles[0] ? model.parentScaleItems : model.studentScaleItems;
  if (scaleItems.length === 0) {
    throw new Error(`No scale items mapped for role ${role}.`);
  }

  for (let i = 0; i < delta; i += 1) {
    const response = form.createResponse();
    response.withItemResponse(model.roleItem.createResponse(role));

    scaleItems.forEach((item) => {
      response.withItemResponse(item.createResponse(drawWeightedScore_()));
    });

    response.submit();
  }

  const summaryAfter = getFormSummary_();
  Logger.log(JSON.stringify({
    added: delta,
    role,
    before: summaryBefore,
    after: summaryAfter,
  }, null, 2));
  return summaryAfter;
}

function submitRoleUntilCount(options) {
  const settings = options || {};
  const targetCount = Number(settings.targetCount);
  const role = normalizeRole_(settings.role);

  if (!Number.isFinite(targetCount) || targetCount < 0) {
    throw new Error('targetCount must be a non-negative number.');
  }
  if (!CONFIG.allowedRoles.includes(role)) {
    throw new Error(`role must be one of: ${CONFIG.allowedRoles.join(', ')}`);
  }

  const form = FormApp.openById(CONFIG.formId);
  const model = buildFormModel_(form);
  const summaryBefore = getFormSummary_();
  const currentCount = summaryBefore[role];
  const delta = targetCount - currentCount;

  if (delta < 0) {
    throw new Error(`Current ${role} count ${currentCount} already exceeds target ${targetCount}.`);
  }
  if (delta === 0) {
    Logger.log('Nothing to add. Target already satisfied.');
    return summaryBefore;
  }

  const scaleItems = role === CONFIG.allowedRoles[0] ? model.parentScaleItems : model.studentScaleItems;
  for (let i = 0; i < delta; i += 1) {
    const response = form.createResponse();
    response.withItemResponse(model.roleItem.createResponse(role));
    scaleItems.forEach((item) => {
      response.withItemResponse(item.createResponse(drawWeightedScore_()));
    });
    response.submit();
  }

  const summaryAfter = getFormSummary_();
  Logger.log(JSON.stringify({
    added: delta,
    role,
    before: summaryBefore,
    after: summaryAfter,
  }, null, 2));
  return summaryAfter;
}

function previewGarbageResponses() {
  const form = FormApp.openById(CONFIG.formId);
  const model = buildFormModel_(form);
  const garbage = listGarbageResponses_(form, model);
  const sheetRows = listGarbageSheetRows_(form);

  const result = {
    garbageResponseCount: garbage.length,
    garbageResponses: garbage,
    garbageSheetRowCount: sheetRows.length,
    garbageSheetRows: sheetRows,
  };

  Logger.log(JSON.stringify(result, null, 2));
  return result;
}

function deleteGarbageResponses() {
  const form = FormApp.openById(CONFIG.formId);
  const model = buildFormModel_(form);
  const garbage = listGarbageResponses_(form, model);

  garbage.forEach((entry) => {
    form.deleteResponse(entry.responseId);
  });

  const deletedSheetRows = deleteGarbageSheetRows_(form);
  const result = {
    deletedFormResponses: garbage.length,
    deletedSheetRows,
  };

  Logger.log(JSON.stringify(result, null, 2));
  return result;
}

function getFormSummary() {
  const result = getFormSummary_();
  Logger.log(JSON.stringify(result, null, 2));
  return result;
}

function getFormSummary_() {
  const form = FormApp.openById(CONFIG.formId);
  const model = buildFormModel_(form);
  const counts = {
    total: 0,
    validTotal: 0,
    학부모: 0,
    학생: 0,
    garbage: 0,
  };

  form.getResponses().forEach((response) => {
    counts.total += 1;
    const audit = auditResponse_(response, model);
    if (audit.reasons.length > 0) {
      counts.garbage += 1;
      return;
    }
    counts[audit.role] += 1;
    counts.validTotal += 1;
  });

  return counts;
}

function buildFormModel_(form) {
  let currentSectionTitle = '';
  let roleItem = null;
  const parentScaleItems = [];
  const studentScaleItems = [];

  form.getItems().forEach((item) => {
    const itemType = item.getType();

    if (itemType === FormApp.ItemType.PAGE_BREAK) {
      currentSectionTitle = item.asPageBreakItem().getTitle() || '';
      return;
    }

    const title = item.getTitle() || '';
    if (itemType === FormApp.ItemType.MULTIPLE_CHOICE && title.includes(CONFIG.roleQuestionKeyword)) {
      roleItem = item.asMultipleChoiceItem();
      return;
    }

    if (itemType !== FormApp.ItemType.SCALE) {
      return;
    }

    if (currentSectionTitle.includes(CONFIG.parentSectionKeyword)) {
      parentScaleItems.push(item.asScaleItem());
      return;
    }

    if (currentSectionTitle.includes(CONFIG.studentSectionKeyword)) {
      studentScaleItems.push(item.asScaleItem());
    }
  });

  if (!roleItem) {
    throw new Error('Role question not found.');
  }
  if (parentScaleItems.length === 0 || studentScaleItems.length === 0) {
    throw new Error('Could not map scale items for both parent and student sections.');
  }

  return {
    roleItem,
    parentScaleItems,
    studentScaleItems,
  };
}

function listGarbageResponses_(form, model) {
  return form.getResponses()
    .map((response) => auditResponse_(response, model))
    .filter((audit) => audit.reasons.length > 0);
}

function auditResponse_(response, model) {
  const roleResponse = response.getResponseForItem(model.roleItem);
  const role = normalizeRole_(roleResponse ? roleResponse.getResponse() : '');
  const answeredItemIds = new Set(
    response.getItemResponses()
      .filter((itemResponse) => hasMeaningfulResponse_(itemResponse.getResponse()))
      .map((itemResponse) => itemResponse.getItem().getId())
  );

  const parentAnswerCount = model.parentScaleItems.filter((item) => answeredItemIds.has(item.getId())).length;
  const studentAnswerCount = model.studentScaleItems.filter((item) => answeredItemIds.has(item.getId())).length;
  const reasons = [];

  if (!CONFIG.allowedRoles.includes(role)) {
    reasons.push('invalid-role');
  }
  if (role === CONFIG.allowedRoles[0] && studentAnswerCount > 0) {
    reasons.push('parent-role-with-student-answers');
  }
  if (role === CONFIG.allowedRoles[1] && parentAnswerCount > 0) {
    reasons.push('student-role-with-parent-answers');
  }
  if (parentAnswerCount > 0 && studentAnswerCount > 0) {
    reasons.push('answers-in-both-sections');
  }

  return {
    responseId: response.getId(),
    timestamp: response.getTimestamp(),
    role,
    parentAnswerCount,
    studentAnswerCount,
    reasons,
  };
}

function listGarbageSheetRows_(form) {
  if (form.getDestinationType() !== FormApp.DestinationType.SPREADSHEET) {
    return [];
  }

  const sheet = SpreadsheetApp.openById(form.getDestinationId()).getSheets()[0];
  const values = sheet.getDataRange().getValues();
  if (values.length < 2) {
    return [];
  }

  const header = values[0].map(String);
  const roleColumnIndex = findRoleColumnIndex_(header);
  if (roleColumnIndex === -1) {
    throw new Error('Could not find the role column in the linked response sheet.');
  }

  const rows = [];
  for (let rowIndex = 1; rowIndex < values.length; rowIndex += 1) {
    const role = normalizeRole_(values[rowIndex][roleColumnIndex]);
    if (CONFIG.allowedRoles.includes(role)) {
      continue;
    }

    rows.push({
      rowNumber: rowIndex + 1,
      timestamp: values[rowIndex][0],
      role,
    });
  }

  return rows;
}

function deleteGarbageSheetRows_(form) {
  if (form.getDestinationType() !== FormApp.DestinationType.SPREADSHEET) {
    return 0;
  }

  const sheet = SpreadsheetApp.openById(form.getDestinationId()).getSheets()[0];
  const garbageRows = listGarbageSheetRows_(form);

  garbageRows
    .sort((a, b) => b.rowNumber - a.rowNumber)
    .forEach((entry) => {
      sheet.deleteRow(entry.rowNumber);
    });

  return garbageRows.length;
}

function findRoleColumnIndex_(header) {
  return header.findIndex((name) => name.includes(CONFIG.roleQuestionKeyword));
}

function drawWeightedScore_() {
  const totalWeight = CONFIG.scoreWeights.reduce((sum, entry) => sum + entry.weight, 0);
  let cursor = Math.random() * totalWeight;

  for (let i = 0; i < CONFIG.scoreWeights.length; i += 1) {
    cursor -= CONFIG.scoreWeights[i].weight;
    if (cursor <= 0) {
      return CONFIG.scoreWeights[i].score;
    }
  }

  return CONFIG.scoreWeights[CONFIG.scoreWeights.length - 1].score;
}

function normalizeRole_(value) {
  return String(value || '').trim();
}

function hasMeaningfulResponse_(value) {
  if (value === null || value === undefined) {
    return false;
  }
  if (Array.isArray(value)) {
    return value.length > 0;
  }
  return String(value).trim() !== '';
}
