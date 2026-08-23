def build_p2_vlm_context(p2_result: dict) -> str:
    """
    Builds a plain-text context string from P2 perception results.
    """
    if not p2_result:
        return ""
        
    lines = [
        "[EXTERNAL PERCEPTION CONTEXT]",
        "This information was produced by an external perception model and should",
        "be used as supporting information."
    ]
    
    p2_task = p2_result.get("p2_task")
    
    if p2_task == "change_detection":
        lines.append("The P2 change-detection pipeline generated a change mask.")
    elif p2_task == "optical_segmentation":
        lines.append("The P2 optical-segmentation pipeline generated a feature mask.")
    elif p2_task == "optical_sar_fusion":
        lines.append("The P2 optical-SAR pipeline generated a fusion mask.")
    else:
        if p2_task:
            lines.append(f"The P2 {p2_task} pipeline executed.")
        else:
            lines.append("The P2 pipeline executed.")
        
    conf = p2_result.get("p2_confidence")
    if conf is not None:
        lines.append(f"Perception confidence: {conf}")
        
    metrics = p2_result.get("p2_metrics", {})
    if metrics:
        iou = metrics.get("sensor_agreement_iou")
        if iou is not None:
            lines.append(f"Sensor agreement IoU: {iou}")
        cp = metrics.get("cloud_penalty")
        if cp is not None:
            lines.append(f"Cloud penalty: {cp}")
        tp = metrics.get("terrain_penalty")
        if tp is not None:
            lines.append(f"Terrain penalty: {tp}")
            
    return "\n".join(lines)
