using UnityEngine;

/// <summary>
/// Управление камерой: вращение вокруг установки + зум.
/// </summary>
public class CameraOrbit : MonoBehaviour
{
    public Transform target;
    public float distance = 10f;
    public float minDistance = 3f;
    public float maxDistance = 25f;
    public float rotationSpeed = 2f;
    public float zoomSpeed = 5f;
    public float minY = 5f;
    public float maxY = 85f;

    private float currentX = 45f;
    private float currentY = 30f;

    void Start()
    {
        if (target == null)
            target = GameObject.Find("Flare_Stack")?.transform;
    }

    void Update()
    {
        if (Input.GetMouseButton(1)) // Правая кнопка мыши — вращение
        {
            currentX += Input.GetAxis("Mouse X") * rotationSpeed;
            currentY -= Input.GetAxis("Mouse Y") * rotationSpeed;
            currentY = Mathf.Clamp(currentY, minY, maxY);
        }

        float scroll = Input.GetAxis("Mouse ScrollWheel");
        distance -= scroll * zoomSpeed;
        distance = Mathf.Clamp(distance, minDistance, maxDistance);
    }

    void LateUpdate()
    {
        if (target == null) return;

        Quaternion rotation = Quaternion.Euler(currentY, currentX, 0);
        Vector3 negDistance = new Vector3(0, 0, -distance);
        Vector3 position = rotation * negDistance + target.position;

        transform.position = position;
        transform.LookAt(target.position + Vector3.up * 3f);
    }
}
