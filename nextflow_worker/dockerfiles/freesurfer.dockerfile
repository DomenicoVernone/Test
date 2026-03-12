FROM freesurfer/freesurfer:7.2.0

ARG LICENSE_FILE=license.txt
COPY ${LICENSE_FILE} /usr/local/freesurfer/.license

CMD [ "bash" ]