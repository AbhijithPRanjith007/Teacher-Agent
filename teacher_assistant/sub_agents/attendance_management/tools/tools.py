from datetime import datetime
from typing import List, Dict, Optional


def mark_attendance(student_id: str, class_id: str, status: str = "present") -> dict:
    """Mark attendance for a student in a specific class."""
    print(f"--- Tool: mark_attendance called for student {student_id} ---")
    
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Validate status
        valid_statuses = ["present", "absent", "late", "excused"]
        if status.lower() not in valid_statuses:
            return {
                "status": "error",
                "error_message": f"Invalid attendance status. Must be one of: {valid_statuses}",
            }
        
        return {
            "status": "success",
            "student_id": student_id,
            "class_id": class_id,
            "attendance_status": status.lower(),
            "date": current_date,
            "timestamp": current_time,
            "message": f"Attendance marked for student {student_id} as {status.lower()}"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Error marking attendance: {str(e)}",
        }


def get_attendance_report(class_id: str, date: Optional[str] = None) -> dict:
    """Get attendance report for a specific class and date."""
    print(f"--- Tool: get_attendance_report called for class {class_id} ---")
    
    try:
        report_date = date if date else datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Mock data - in real implementation, this would fetch from database
        sample_report = {
            "total_students": 25,
            "present": 22,
            "absent": 2,
            "late": 1,
            "excused": 0,
            "attendance_rate": 88.0
        }
        
        return {
            "status": "success",
            "class_id": class_id,
            "date": report_date,
            "timestamp": current_time,
            "report": sample_report,
            "message": f"Attendance report generated for class {class_id} on {report_date}"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Error generating attendance report: {str(e)}",
        }


def check_student_attendance(student_id: str, date_range: Optional[str] = None) -> dict:
    """Check attendance history for a specific student."""
    print(f"--- Tool: check_student_attendance called for student {student_id} ---")
    
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Mock data - in real implementation, this would fetch from database
        attendance_history = [
            {"date": "2024-01-15", "status": "present", "class_id": "MATH101"},
            {"date": "2024-01-16", "status": "absent", "class_id": "MATH101"},
            {"date": "2024-01-17", "status": "late", "class_id": "MATH101"},
            {"date": "2024-01-18", "status": "present", "class_id": "MATH101"},
            {"date": "2024-01-19", "status": "present", "class_id": "MATH101"},
        ]
        
        total_days = len(attendance_history)
        present_days = len([day for day in attendance_history if day["status"] in ["present", "late"]])
        attendance_percentage = (present_days / total_days) * 100 if total_days > 0 else 0
        
        return {
            "status": "success",
            "student_id": student_id,
            "timestamp": current_time,
            "attendance_history": attendance_history,
            "summary": {
                "total_days": total_days,
                "present_days": present_days,
                "attendance_percentage": round(attendance_percentage, 2)
            },
            "message": f"Attendance history retrieved for student {student_id}"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Error checking student attendance: {str(e)}",
        }


def bulk_attendance_upload(attendance_data: List[Dict]) -> dict:
    """Upload attendance data for multiple students at once."""
    print(f"--- Tool: bulk_attendance_upload called for {len(attendance_data)} records ---")
    
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        successful_uploads = 0
        failed_uploads = 0
        errors = []
        
        for record in attendance_data:
            # Validate required fields
            required_fields = ["student_id", "class_id", "status"]
            missing_fields = [field for field in required_fields if field not in record]
            
            if missing_fields:
                failed_uploads += 1
                errors.append(f"Missing fields {missing_fields} in record: {record}")
            else:
                successful_uploads += 1
        
        return {
            "status": "success" if failed_uploads == 0 else "partial_success",
            "timestamp": current_time,
            "total_records": len(attendance_data),
            "successful_uploads": successful_uploads,
            "failed_uploads": failed_uploads,
            "errors": errors,
            "message": f"Processed {len(attendance_data)} attendance records"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Error in bulk attendance upload: {str(e)}",
        }