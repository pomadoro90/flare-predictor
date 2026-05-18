using UnityEngine;
using UnityEngine.UI;
using TMPro;

/// <summary>
/// Переключение между режимами «Архив» и «Раннее предупреждение».
/// </summary>
public class ModeSwitch : MonoBehaviour
{
    public GameObject archivePanel;
    public GameObject earlyWarningPanel;
    public Button archiveButton;
    public Button earlyWarningButton;

    public enum Mode { Archive, EarlyWarning }
    public Mode currentMode { get; private set; } = Mode.Archive;

    void Start()
    {
        archiveButton.onClick.AddListener(() => SwitchTo(Mode.Archive));
        earlyWarningButton.onClick.AddListener(() => SwitchTo(Mode.EarlyWarning));
        SwitchTo(Mode.Archive);
    }

    void SwitchTo(Mode mode)
    {
        currentMode = mode;
        bool isArchive = mode == Mode.Archive;

        archivePanel.SetActive(isArchive);
        earlyWarningPanel.SetActive(!isArchive);

        // Подсветка активной кнопки
        Color active = new Color(0.42f, 0.39f, 1f);     // #6C63FF
        Color inactive = new Color(0.3f, 0.3f, 0.35f);

        var archiveColors = archiveButton.colors;
        archiveColors.normalColor = isArchive ? active : inactive;
        archiveButton.colors = archiveColors;

        var ewColors = earlyWarningButton.colors;
        ewColors.normalColor = !isArchive ? active : inactive;
        earlyWarningButton.colors = ewColors;
    }
}
