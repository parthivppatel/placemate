from django.utils.html import escape
from django.core.mail import send_mail
from placemate import settings
from ..schema.company_drive_jobs import CompanyDriveJobs
import logging

def send_custom_email(email, subject, message, html_message=None):
    """
    Sends an email with both plaintext and HTML versions.
    
    :param email: Recipient email address
    :param subject: Email subject
    :param message: Plain text message (fallback for non-HTML email clients)
    :param html_message: HTML formatted message (optional)
    """
    send_mail(
        subject,
        message,  
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
        html_message=html_message or message,  
    )

def send_otp_email(email, otp):
    """
    Sends a password reset OTP email.
    
    :param email: Recipient email address
    :param otp: One-time password
    """
    subject = "Password Reset OTP - Placemate"
    message = (
        f"Dear {email},\n"
        f"Your OTP for password reset is: {otp}\n"
        "This OTP is valid for 1 minute.\n"
        "If you did not request this, please ignore this email."
    )

    html_message = f"""
        <html>
        <body>
            <p>Dear {escape(email)},</p>
            <p>Your OTP for password reset is: <strong>{escape(otp)}</strong></p>
            <p>This OTP is valid for <strong>1 minute</strong>.</p>
            <p>If you did not request this, please ignore this email.</p>
            <br>
            <p>Best Regards,</p>
            <p><strong>Placemate Team</strong></p>
        </body>
        </html>
    """

    send_custom_email(email, subject, message, html_message)

def send_welcome_email(email, username):
    """
    Sends a welcome email to a new user.
    
    :param email: Recipient email address
    :param username: Name of the user
    """
    subject = "Welcome to Placemate!"
    message = f"Hello {username},\nWelcome to Placemate! We're excited to have you on board."

    html_message = f"""
        <html>
        <body>
            <p>Hello {escape(username)},</p>
            <p>Welcome to <strong>Placemate</strong>! We're excited to have you on board.</p>
            <br>
            <p>Best Regards,</p>
            <p><strong>Placemate Team</strong></p>
        </body>
        </html>
    """

    send_custom_email(email, subject, message, html_message)

def send_registration_email(email, password):
    subject = "Welcome to Placemate - Your Company Registration Details"
    message = f"Hello {email},\nWelcome to Placemate! We're excited to have you on board."

    html_message = f"""
    <html>
    <body>
        <p>Dear User,</p>

        <p>Welcome to <strong>Placemate</strong>! Your company registration is successful.</p>

        <p><strong>Here are your login credentials:</strong></p>
        <ul>
            <li><strong>Email:</strong> {email}</li>
            <li><strong>Password:</strong> {password}</li>
        </ul>

        <p>You can log in using the following link:</p>
        <p><a href="http://127.0.0.1:8000/login" target="_blank"><strong>Placemate</strong></a></p>

        <p>Please use these credentials to log in and complete your profile.</p>

        <p>If you have any questions, feel free to contact us.</p>

        <p>Best regards,<br>
        <strong>Placemate Team</strong></p>
    </body>
    </html>
    """

    send_custom_email(email,subject,message,html_message)


def send_drive_emails(drive, students,jobs,skills,courses,locations,edit=False):
    logger = logging.getLogger(__name__)

    try:
        company = drive.company
        # drive_jobs = Job.objects.filter(company=company)
        # jobs = [cdj for cdj in companydrivejobs]
        # jobs = CompanyDriveJobs.objects.filter(id__in=job_ids)

        job_lines = ""
        for i, job in enumerate(jobs, start=1):
            job_lines += f"{i}. <strong>{job['job_title']}</strong>: {job['job_description']}<br>"

        update_msg = ""
        if edit:
            update_msg =f"""
            <div style="padding: 12px 16px; background-color: #fff8e1; border-left: 5px solid #fbc02d; margin-bottom: 20px;">
              <p style="margin: 0; font-size: 15px; color: #333;">
                <strong>Note:</strong> There has been an update to this drive.<br>
                Please review the latest details below. 
              </p>
            </div>""" 


        subject = f"Placement Drive - {company.name} - {drive.drive_name}"
 
        message_html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
            <p>Dear Students,</p>
            {update_msg}
            <p>
              Upcoming placement drive of the company <strong>{company.name}</strong>
              is scheduled on <strong>{f"{drive.start_date.strftime('%Y')}-00-00:00:00"}</strong>.
            </p>

            <h3>Details of the drive and eligibility criteria:</h3>
            <ul style="list-style-type: none; padding: 0; margin: 0; font-family: Arial, sans-serif; color: #333;">
            <li><strong>Registration Starts on:</strong> {f"{drive.start_date.strftime('%Y-%m-%d %H:%M')}:00"}</li>
            <li><strong>Registration Ends on:</strong> {f"{drive.end_date.strftime('%Y-%m-%d %H:%M')}:00"}</li>
            <li><strong>Offer Type:</strong> {drive.job_type}</li>
            <li><strong>Category:</strong> {company.category}</li>
            <li><strong>Mode:</strong> {drive.job_mode}</li>
            <li><strong>Bond details:</strong> {drive.bond or '-'}</li>
            <li><strong>Skills Required:</strong> {', '.join(skills) if skills else "-" }</li>
            <li><strong>Open for:</strong> {', '.join(courses) if courses else "-"}</li>
            <li><strong>Posting Location(s) :</strong> {', '.join(locations) if locations else "-"}</li>
            </ul>

            <h3>Company Profile Details:</h3>
            <p><strong>Name:</strong> {company.name}</p>
            <p><strong>Description:</strong><br />{company.description or '-'}</p>

            <h3>Job Roles:</h3>
            <p>{job_lines}</p>

            <ul style="list-style-type: none; padding: 0; margin: 0; font-family: Arial, sans-serif; color: #333;">            
            <li><strong>UG Package(LPA):</strong> {
                f"{drive.ug_package_min} - {drive.ug_package_max}"
                if drive.ug_package_min and drive.ug_package_max
                else "-"}</li>
            <li><strong>PG Package(LPA):</strong>{ 
                  f"{drive.pg_package_min} - {drive.pg_package_max}"
                if drive.pg_package_min and drive.pg_package_max
                else "-"}
            </li>
            <li><strong>Stipend:</strong> ₹{drive.stipend or '-'}</li>
            </ul>

            <p>
              <strong>Note:</strong> All the students who are registering for a company are required
              to attend the company process and cannot back out from the same, for any reason.
              Anyone violating this norm will be strictly banned from the next eligible company.
            </p>

            <p>
              <strong>Strict notice to all the students:</strong> No late registrations will be entertained
              (no matter the reason). So, do keep in mind the registration deadline.
              Research about the company and the job profile before registering.
            </p>

            <p>Wish you luck!</p>

            <p><strong>Regards,<br />Student Placement Cell</strong></p>
          </body>
        </html>
        """

        message = "Hello There is companyDrive Details"
        email_list = [s.student_id.email for s in students]

        # print(email_list)
        for email in email_list:
            send_custom_email(email,subject,message,message_html)

    except Exception as e:
        logger.error(f"Error : {str(e)}", exc_info=True)

def send_student_registration_email(email, password):
    subject = "Welcome to Placemate - Your Company Registration Details"
    message = f"Hello {email},\nWelcome to Placemate! We're excited to have you on board."

    html_message = f"""
    <html>
    <body>
        <p>Dear User,</p>

        <p>Welcome to <strong>Placemate</strong>! Your registration is successful.</p>

        <p><strong>Here are your login credentials:</strong></p>
        <ul>
            <li><strong>Email:</strong> {email}</li>
            <li><strong>Password:</strong> {password}</li>
        </ul>

        <p>You can log in using the following link:</p>
        <p><a href="http://127.0.0.1:8000/login" target="_blank"><strong>Placemate</strong></a></p>

        <p>Please use these credentials to log in and complete your profile.</p>

        <p>If you have any questions, feel free to contact us.</p>

        <p>Best regards,<br>
        <strong>Placemate Team</strong></p>
    </body>
    </html>
    """

    send_custom_email(email,subject,message,html_message)