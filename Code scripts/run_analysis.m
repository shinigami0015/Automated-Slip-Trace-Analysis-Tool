% =========================================================================
% run_analysis.m  — ASTA Tool UI Wrapper Entry Point
% =========================================================================
%
% This script is called by the ASTA Tool Python UI via:
%   eng.eval('run_analysis', nargout=0)
%
% The following variables are INJECTED into the workspace by the Python
% side BEFORE this script is called (do NOT hardcode them here):
%
%   inputDir         — path to folder containing .ctf files
%   outputBaseDir    — path to base output folder
%   loadDirChoice    — loading direction: 'X', 'Y', or 'Z'
%   ca_ratio         — c/a ratio (e.g. 1.5930)
%   crystalSystemMode — 0 = HCP+BCC, 1 = HCP only, 2 = BCC only
%
% This wrapper:
%   1. Preserves the injected variables across startup_mtex + clear
%   2. Maps loadDirChoice string → vector3d
%   3. Calls the main analysis pipeline (main.m logic is inlined below
%      or you can source main.m after variable injection)
%
% HOW TO USE:
%   Option A (recommended): Place this file alongside main.m.
%                           The UI will call run_analysis automatically.
%   Option B:               Rename main.m to run_analysis.m and remove the
%                           hardcoded inputDir/outputBaseDir lines from it.
%
% =========================================================================

% ── 1. Capture injected variables before any clear ───────────────────────
%    (startup_mtex does not call clear, but main.m does — so we save them)
temp_inputDir         = inputDir;
temp_outputBaseDir    = outputBaseDir;
temp_loadDirChoice    = loadDirChoice;
temp_ca_ratio         = ca_ratio;
temp_crystalSystemMode = crystalSystemMode;

% ── 2. Initialise MTEX ───────────────────────────────────────────────────
if exist('check_mtex', 'file') == 0
    try
        startup_mtex
    catch
        addpath('D:\Abhinav Chandraker (Pls do not delete)\Zr alloy\Zr slip trace\codes\MTEX\mtex-6.0.0\mtex-6.0.0');
        startup_mtex
    end
end
clc;
% NOTE: we do NOT call "clear" here so variables are preserved.

% ── 3. Restore variables (safe regardless of whether clear was called) ───
inputDir         = temp_inputDir;
outputBaseDir    = temp_outputBaseDir;
loadDirChoice    = temp_loadDirChoice;
ca_ratio         = temp_ca_ratio;
crystalSystemMode = temp_crystalSystemMode;

% ── 4. Map loading direction string to vector3d ──────────────────────────
switch upper(strtrim(loadDirChoice))
    case 'X'
        loaddir = vector3d.X;
    case 'Y'
        loaddir = vector3d.Y;
    case 'Z'
        loaddir = vector3d.Z;
    otherwise
        warning('Unknown loading direction "%s", defaulting to X.', loadDirChoice);
        loaddir = vector3d.X;
end

disp(['run_analysis: inputDir      = ', inputDir]);
disp(['run_analysis: outputBaseDir = ', outputBaseDir]);
disp(['run_analysis: loadDirChoice = ', loadDirChoice]);
disp(['run_analysis: ca_ratio      = ', num2str(ca_ratio)]);

% ── 5. Index all .ctf datasets ──────────────────────────────────────────
ctfFiles = dir(fullfile(inputDir, '*.ctf'));
if isempty(ctfFiles)
    error('No .ctf files found in: %s', inputDir);
end
fprintf('Found %d .ctf file(s).\n', length(ctfFiles));

% ── 6. Define crystal symmetries ────────────────────────────────────────
%    Use ca_ratio for the HCP c-axis length (a=3.26 Angstrom for Zr)
a_hcp = 3.26;
c_hcp = a_hcp * ca_ratio;

cS_hcp = crystalSymmetry('6/mmm', [a_hcp a_hcp c_hcp], ...
    'mineral', 'Zr Nb Alpha HCP', 'X||a*', 'Y||b', 'Z||c');
cS_bcc = crystalSymmetry('m-3m', [3.555 3.555 3.555], ...
    'mineral', 'Zr Nb Beta BCC', 'X||a*', 'Y||b', 'Z||c');
cs = {cS_bcc, cS_hcp};

% ── 7. Phase tracking arrays ─────────────────────────────────────────────
labels_alpha = {'Prismatic', 'Basal', 'Pyramidal <a>', 'Pyramidal I <c+a>', 'Pyramidal II <c+a>'};
combinedSSCounts_alpha = zeros(1, numel(labels_alpha));
totalGrains_alpha = 0;

labels_beta = {'{110}<111>', '{112}<111>', '{123}<111>'};
combinedSSCounts_beta = zeros(1, numel(labels_beta));
totalGrains_beta = 0;

z = vector3d.Z;

% ── 8. Main processing loop ───────────────────────────────────────────────
for k = 1:length(ctfFiles)
    ctfPath = fullfile(ctfFiles(k).folder, ctfFiles(k).name);
    [~, sampleName, ~] = fileparts(ctfFiles(k).name);
    fprintf('\n=== Processing [%d/%d]: %s ===\n', k, length(ctfFiles), sampleName);

    % Raw orientation map
    EBSD_crystal_orientation_image(ctfPath, cs, outputBaseDir, sampleName, z);

    % EBSD processing
    [ebsd, grains] = EBSD_processing(ctfPath, cs);

    % Crystal shape and IPF keys
    for l = 2:3
        cs0 = ebsd(ebsd.phaseId == l).CS;
        if l == 2
            cs_1 = crystalShape.cube(cs0);
            ipfKey_1 = ipfColorKey(cs0);
            ipfKey_1.inversePoleFigureDirection = z;
        else
            cs_2 = crystalShape.hex(cs0);
            ipfKey_2 = ipfColorKey(cs0);
            ipfKey_2.inversePoleFigureDirection = z;
        end
    end

    % EBSD composite map
    fig_ebsd = figure;
    plot(ebsd(ebsd.phaseId == 2), ebsd(ebsd.phaseId == 2).orientations, ipfKey_1);
    hold on
    plot(ebsd(ebsd.phaseId == 3), ebsd(ebsd.phaseId == 3).orientations, ipfKey_2);
    hold on
    plot(grains.boundary, 'lineColor', [1 0 0], 'linewidth', 2);
    hold on
    plot(grains(grains.phaseId == 2), 0.4*cs_1, 'linewidth', 2, 'colored')
    hold on
    plot(grains(grains.phaseId == 3), 0.4*cs_2, 'linewidth', 2, 'colored')
    hold off
    set(gca, 'YDir', 'reverse');
    legend off
    title('EBSD Map');

    outputFolder = fullfile(outputBaseDir, sampleName);
    if ~exist(outputFolder, 'dir'), mkdir(outputFolder); end
    set(fig_ebsd, 'Units', 'normalized', 'WindowState', 'maximized');
    drawnow;
    exportgraphics(fig_ebsd, fullfile(outputFolder, sprintf('%s_EBSD_Map.png', sampleName)));
    close(fig_ebsd);

    % Phase loops
    for m = 1:2
        phaseLabel = ["Beta", "Alpha"];

        fig_ipdf = figure;
        ebsd_phase = ebsd(ebsd.phaseId == m+1);
        grains_phase = grains(grains.phaseId == m+1);

        % Skip phases excluded by user selection
        if crystalSystemMode == 1 && m == 1   % HCP only — skip Beta
            close(fig_ipdf);
            continue;
        end
        if crystalSystemMode == 2 && m == 2   % BCC only — skip Alpha
            close(fig_ipdf);
            continue;
        end

        plotIPDF(ebsd_phase.orientations, z);
        if m == 1
            title('Inverse Pole Figure - Beta Phase');
        else
            title('Inverse Pole Figure - Alpha Phase');
        end
        set(fig_ipdf, 'Units', 'normalized', 'WindowState', 'maximized');
        drawnow;
        exportgraphics(fig_ipdf, fullfile(outputFolder, sprintf('%s_%s_IPDF.png', sampleName, phaseLabel(m))));
        close(fig_ipdf);

        % IPF Key
        fig_ipfkey = figure;
        if m == 1
            plot(ipfKey_1);
            title('IPF Key - Beta Phase (Z Direction)');
        else
            plot(ipfKey_2);
            title('IPF Key - Alpha Phase (Z Direction)');
        end
        set(fig_ipfkey, 'Units', 'normalized', 'WindowState', 'maximized');
        drawnow;
        exportgraphics(fig_ipfkey, fullfile(outputFolder, sprintf('%s_%s_IPF_Key.png', sampleName, phaseLabel(m))));
        close(fig_ipfkey);

        if m == 1
            ipfColor = ipfKey_1.orientation2color(ebsd_phase.orientations);
        else
            ipfColor = ipfKey_2.orientation2color(ebsd_phase.orientations);
        end

        % Slip traces
        fig_trace = figure;
        plot(ebsd_phase, ipfColor);
        hold on;
        plot(grains.boundary, 'lineColor', 'k', 'lineWidth', 1.5);
        [schmidfactors, grainIDs, schmidFactors, slipSystems, slipFamilies, traceAngles, traceAngles_fin, q, qx, qy] = ...
            slip_trace(ebsd_phase, grains_phase, loaddir, cs, m);
        set(gca, 'YDir', 'reverse');
        title(sprintf('Slip Traces - %s Phase', phaseLabel(m)));
        hold off;
        set(fig_trace, 'Units', 'normalized', 'WindowState', 'maximized');
        drawnow;
        exportgraphics(fig_trace, fullfile(outputFolder, sprintf('%s_%s_SlipTraces.png', sampleName, phaseLabel(m))));
        close(fig_trace);

        % Grain ID map
        fig_grain_ids = figure;
        plot(ebsd_phase, ipfColor);
        hold on;
        plot(grains_phase.boundary, 'lineColor', 'k', 'lineWidth', 1.5);
        for i = 1:length(grains_phase)
            text(grains_phase(i).centroid.x, grains_phase(i).centroid.y, ...
                num2str(grains_phase(i).id), ...
                'FontSize', 8, 'FontWeight', 'bold', 'color', 'k', ...
                'HorizontalAlignment', 'center', 'BackgroundColor', 'w', 'EdgeColor', 'k', 'Margin', 1);
        end
        set(gca, 'YDir', 'reverse');
        title(sprintf('Grain ID Map - %s Phase', phaseLabel(m)));
        hold off;
        set(fig_grain_ids, 'Units', 'normalized', 'WindowState', 'maximized');
        drawnow;
        exportgraphics(fig_grain_ids, fullfile(outputFolder, sprintf('%s_%s_GrainID_Map.png', sampleName, phaseLabel(m))));
        close(fig_grain_ids);

        % CSV export
        valid = ~isnan(grainIDs);
        T = table(grainIDs(valid), schmidFactors(valid), slipSystems(valid), ...
            slipFamilies(valid), traceAngles(valid), traceAngles_fin(valid), ...
            'VariableNames', {'GrainID', 'SchmidFactor', 'SlipSystem', 'SlipFamily', 'TraceAngle_deg', 'TraceAngle_deg_fin'});

        tablePath = fullfile(outputFolder, sprintf('%s_%s_Grain_Slip_Data.csv', sampleName, phaseLabel(m)));
        writetable(T, tablePath);

        uniqueGrains = unique(T.GrainID);
        isMax = false(height(T), 1);
        for i = 1:length(uniqueGrains)
            thisGrain = uniqueGrains(i);
            rows = find(T.GrainID == thisGrain);
            if ~isempty(rows)
                [~, relIdx] = max(T.SchmidFactor(rows));
                isMax(rows(relIdx)) = true;
            end
        end
        T.IsMaxSchmid = isMax;
        writetable(T, tablePath);

        % Slip system distribution
        [ss, ~] = slip_systems(cs, m);
        full_sf_map = computeSchmidFactors(ebsd_phase.orientations, loaddir, ss);
        ssCounts = slipsystemdist(full_sf_map, ebsd_phase, grains_phase, cs, m);

        if m == 1
            combinedSSCounts_beta  = combinedSSCounts_beta  + ssCounts;
            totalGrains_beta       = totalGrains_beta       + length(grains_phase);
        else
            combinedSSCounts_alpha = combinedSSCounts_alpha + ssCounts;
            totalGrains_alpha      = totalGrains_alpha      + length(grains_phase);
        end
    end
end
close all;

% ── 9. Combined bar chart ─────────────────────────────────────────────────
combinedCounts = [combinedSSCounts_alpha, 0, combinedSSCounts_beta];
xtickLabels = [labels_alpha, {''}, labels_beta];

figure;
bar(combinedCounts, 'FaceColor', [0.2 0.5 0.7]);
xticks(1:length(combinedCounts));
xticklabels(xtickLabels);
ylabel('Number of Grains with Active Slip System');
title('Aggregated Slip System Activation - \alpha & \beta Phases');
xtickangle(45);
grid on;

annotationText_alpha = sprintf('\\alpha - Total Grains: %d', totalGrains_alpha);
annotationText_beta  = sprintf('\\beta - Total Grains: %d',  totalGrains_beta);

annotation('textbox', [0.15 0.85 0.3 0.07], 'String', annotationText_alpha, ...
    'FontSize', 12, 'FontWeight', 'bold', 'EdgeColor', 'black', 'BackgroundColor', 'white');
annotation('textbox', [0.55 0.85 0.3 0.07], 'String', annotationText_beta, ...
    'FontSize', 12, 'FontWeight', 'bold', 'EdgeColor', 'black', 'BackgroundColor', 'white');

xline(numel(labels_alpha) + 0.5, '--k', 'LineWidth', 1.2);

set(gcf, 'Units', 'normalized', 'WindowState', 'maximized');
drawnow;

% Save to the last outputFolder (or outputBaseDir if no samples)
if exist('outputFolder', 'var')
    savePath = outputFolder;
else
    savePath = outputBaseDir;
end
exportgraphics(gcf, fullfile(savePath, 'Combined_SlipSystem_vs_Grains_AlphaBeta.png'));

fclose('all');
close all;
disp('run_analysis: Processing Complete. All files released.');
