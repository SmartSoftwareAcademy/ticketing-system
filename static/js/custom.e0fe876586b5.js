function getValue() {
    console.log('js loaded')
    close_ticket_check = document.getElementById("closeticket")
    if (close_ticket_check.checked == True) {
        close_ticket_check.value = 'True'
        console.log(close_ticket_check)
    } else {
        close_ticket_check.value = 'False'
        console.log(close_ticket_check)
    }
}