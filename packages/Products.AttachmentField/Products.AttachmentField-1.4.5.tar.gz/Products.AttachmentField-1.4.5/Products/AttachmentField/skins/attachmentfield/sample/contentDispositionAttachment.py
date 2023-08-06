request = context.REQUEST
response = request.RESPONSE
response.setHeader(
    'Content-Disposition',
    'attachment; filename="sampleFileName.txt"'
)
response.setHeader('Content-Type', "text/plain")
response.write("I am some sample data :-)\n\n")
