<jsp:
out.println(request.getParameter("test"));

<!--CVI-170001-->
include(request.getParam('test'));

<!--CVI-140001-->
<input type="hidden" value="request.getParameter("test")">